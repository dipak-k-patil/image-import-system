# API Documentation

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
