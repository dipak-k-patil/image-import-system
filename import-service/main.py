import os
import redis
import json
import boto3
import requests
import io
import mimetypes
import uuid
import dropbox
from google.oauth2 import service_account
from concurrent.futures import ThreadPoolExecutor
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from common.models import Base, Image, SessionLocal

load_dotenv()

# Worker Configuration
WORKER_COUNT = int(os.getenv("WORKER_COUNT", 10))

# Redis Configuration
redis_url = os.getenv("REDIS_URL")
r = redis.from_url(redis_url)

# S3 Configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
)
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
# Google Drive Configuration
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

GOOGLE_CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not GOOGLE_CREDS_PATH:
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set")

creds = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDS_PATH,
    scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=creds)


# Dropbox Configuration
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

dbx = dropbox.Dropbox(
    oauth2_access_token=DROPBOX_ACCESS_TOKEN
)


def process_google_drive_folder(folder_url):
    folder_id = folder_url.rstrip("/").split("/")[-1]
    page_token = None
    while True:
        results = (
            drive_service.files()
            .list(
                q=f"'{folder_id}' in parents and mimeType contains 'image/'",
                fields="nextPageToken, files(id, name, mimeType, size)",
                pageToken=page_token,
            )
            .execute()
        )
        items = results.get("files", [])
        for item in items:
            r.lpush("image_processing_jobs", json.dumps({"source": "google_drive", "item": item}))
        page_token = results.get("nextPageToken", None)
        if page_token is None:
            break


# NOTE: This processes only top-level files.
# Recursive folder traversal can be added if required.

def process_dropbox_folder(url):
    metadata = dbx.sharing_get_shared_link_metadata(url)
    folder_path = metadata.path_lower

    result = dbx.files_list_folder(folder_path)
    while True:
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                r.lpush(
                    "image_processing_jobs",
                    json.dumps({
                        "source": "dropbox",
                        "entry": entry.to_json(),
                        "url": url
                    })
                )
        if not result.has_more:
            break
        result = dbx.files_list_folder_continue(result.cursor)

def process_image(job_data):
    job = json.loads(job_data)
    source = job["source"]
    db = SessionLocal()
    image = None

    try:
        if source == "google_drive":
            item = job["item"]
            
            # Idempotency check
            existing_image = db.query(Image).filter_by(google_drive_id=item["id"]).first()
            if existing_image:
                print(f"Image {item['name']} already imported.")
                return

            s3_key = f"{uuid.uuid4()}-{item['name']}"
            image = Image(
                name=item["name"],
                google_drive_id=item["id"],
                size=item.get("size", 0),
                mime_type=item["mimeType"],
                source="google_drive",
                status="processing",
            )
            db.add(image)
            db.commit()

            request = drive_service.files().get_media(fileId=item["id"])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)

            s3.upload_fileobj(
             fh,
                S3_BUCKET_NAME,
                s3_key,
                ExtraArgs={"ContentType": item["mimeType"]}
            )

            image.storage_path = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
            image.status = "completed"
            db.commit()

        elif source == "dropbox":
            entry_data = json.loads(job["entry"])
            entry = dropbox.files.FileMetadata.from_json(entry_data)
            
            # Idempotency check
            existing_image = db.query(Image).filter_by(source_file_id=entry.id).first()
            if existing_image:
                print(f"Image {entry.name} already imported.")
                return

            s3_key = f"{uuid.uuid4()}-{entry.name}"
            mime_type, _ = mimetypes.guess_type(entry.name)
            image = Image(
                name=entry.name,
                source_file_id=entry.id,
                size=entry.size,
                mime_type=mime_type,
                source="dropbox",
                status="processing",
            )
            db.add(image)
            db.commit()

            metadata, res = dbx.sharing_get_shared_link_file(url=job["url"], path=f"/{entry.name}")
            s3.upload_fileobj(
                res.raw,
                S3_BUCKET_NAME,
                s3_key,
                ExtraArgs={"ContentType": mime_type or "image/jpeg"}
            )

            image.storage_path = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
            image.status = "completed"
            db.commit()

    except Exception as e:
        print(f"Error processing image: {e}")
        if image:
            image.status = "failed"
            db.commit()
    finally:
        db.close()

def folder_processing_worker():
    while True:

        # Blocking call, runs continuously as a worker
        
        _, job_data = r.brpop("import_jobs")
        data = json.loads(job_data)
        folder_url = data["url"]
        source = data["source"]

        print(f"Received {source} import job for: {folder_url}")

        if source == "google_drive":
            process_google_drive_folder(folder_url)
        elif source == "dropbox":
            process_dropbox_folder(folder_url)

def image_processing_worker():
    with ThreadPoolExecutor(max_workers=WORKER_COUNT) as executor:
        while True:
            _, job_data = r.brpop("image_processing_jobs")
            executor.submit(process_image, job_data)

if __name__ == "__main__":
    import threading
    folder_worker_thread = threading.Thread(target=folder_processing_worker)
    image_worker_thread = threading.Thread(target=image_processing_worker)
    folder_worker_thread.start()
    image_worker_thread.start()
