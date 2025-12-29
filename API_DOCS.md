# API Documentation
# Set Up .env file -
# PostgreSQL Database
DATABASE_URL=postgresql://user:password@db:5432/images
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=images

# Redis
REDIS_URL=redis://redis:6379

# AWS S3
S3_BUCKET_NAME=your-s3-bucket-name
S3_AWS_ACCESS_KEY_ID=your-access-key-id
S3_AWS_SECRET_ACCESS_KEY=your-secret-access-key

# Google Drive API
GOOGLE_API_KEY=your-google-api-key

# Dropbox API
DROPBOX_APP_KEY=your-dropbox-app-key
DROPBOX_APP_SECRET=your-dropbox-app-secret
DROPBOX_REFRESH_TOKEN=your-dropbox-refresh-token

# Worker Configuration
WORKER_COUNT=10

## Import from Google Drive

**POST** `/import/google-drive`

**Description:** Triggers the import of images from a public Google Drive folder.

**Request Body:**

```json
"https://drive.google.com/drive/folders/your-folder-id"
```

**cURL Example:**

```bash
curl -X POST -H "Content-Type: application/json" -d '"https://drive.google.com/drive/folders/your-folder-id"' http://localhost:8000/import/google-drive
```

## Import from Dropbox

**POST** `/import/dropbox`

**Description:** Triggers the import of images from a public Dropbox folder.

**Request Body:**

```json
"https://www.dropbox.com/sh/your-folder-id"
```

**cURL Example:**

```bash
curl -X POST -H "Content-Type: application/json" -d '"https://www.dropbox.com/sh/your-folder-id"' http://localhost:8000/import/dropbox
```

## Get All Images

**GET** `/images`

**Description:** Returns a list of all imported images.

**cURL Example:**

```bash
curl -X GET http://localhost:8000/images
```

## Get Images by Source

**GET** `/images/source/{source}`

**Description:** Returns a list of images imported from a specific source.

**cURL Example:**

```bash
curl -X GET http://localhost:8000/images/source/google_drive
```
