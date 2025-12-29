import os
import redis
import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import schemas
import crud
from common.models import Base, SessionLocal, engine

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
r = redis.from_url(redis_url)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/import/google-drive")
def import_google_drive(url: str):
    r.lpush("import_jobs", json.dumps({"url": url, "source": "google_drive"}))
    return {"message": "Import job started", "url": url}

@app.post("/import/dropbox")
def import_dropbox(url: str):
    r.lpush("import_jobs", json.dumps({"url": url, "source": "dropbox"}))
    return {"message": "Import job started", "url": url}

@app.get("/images", response_model=list[schemas.Image])
def read_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_images(db, skip=skip, limit=limit)

@app.get("/images/source/{source}", response_model=list[schemas.Image])
def read_images_by_source(source: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_images_by_source(db, source=source, skip=skip, limit=limit)
