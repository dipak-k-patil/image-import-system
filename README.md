# Scalable Image Import System

**Working Site URL:** [Link to your deployed application]

This project is a scalable backend system for importing images from public Google Drive and Dropbox folders, storing them in cloud object storage, and persisting metadata in a SQL database. It also includes a basic frontend to interact with the system.

## Architecture

The system is designed with a multi-service architecture to ensure scalability, fault-tolerance, and maintainability. The core components are:

- **API Service:** A FastAPI application that exposes a RESTful API for triggering imports and retrieving image data. It communicates with the Import Service via a Redis message queue.
- **Import Service:** A Python service that listens for import jobs on a Redis queue. It's responsible for fetching images from the source (Google Drive or Dropbox), uploading them to cloud storage (e.g., AWS S3), and updating the database with the image metadata.
- **Frontend:** A React application that provides a user interface for importing images and viewing the gallery.
- **Database:** A PostgreSQL database for storing image metadata.
- **Redis:** A message broker for asynchronous communication between the API and Import services.

This decoupled architecture allows each service to be scaled independently. For example, if there's a high volume of import jobs, we can scale up the number of Import Service instances without affecting the API or Frontend.

## Scalability

The system is designed to handle large-scale imports (10,000+ images) efficiently:

- **Asynchronous Processing:** By using a message queue (Redis), the API can quickly accept import requests without blocking, while the heavy lifting is handled by the Import Service in the background.
- **Fan-out Pattern:** The import service uses a fan-out pattern to process images in parallel. When a new folder import is requested, the service lists all the images in the folder and creates individual processing jobs for each image. This allows multiple workers to process images from the same folder concurrently, significantly increasing throughput.
- **Independent Scaling:** Each service is containerized and can be scaled independently based on load.
- **Stateless Services:** Both the API and Import services are stateless, making it easy to run multiple instances behind a load balancer.
- **Cloud-Ready:** The entire system is built with cloud deployment in mind, leveraging Docker and portable configurations.

## Local Setup

1.  **Clone the repository:**
    ```bash
    git clone [your-repo-url]
    cd [your-repo-name]
    ```
2.  **Configure environment variables:**
    - **Backend:** Copy the `.env.example` file at the root of the project to `.env`: `cp .env.example .env`. Open the `.env` file and fill in your credentials for AWS S3, Google Drive API, and Dropbox API.
    - **Frontend:** Navigate to the `frontend` directory. Copy the `.env.example` file to `.env`: `cp .env.example .env`. You can modify the `REACT_APP_API_URL` if your backend is running on a different URL.
    - **Note:** The S3 bucket must be configured for public read access for the images to be viewable in the frontend.
3.  **Build and run the services using Docker Compose:**
4.  # Example .env 

 **PostgreSQL Database
```
DATABASE_URL=postgresql://user:password@db:5432/images
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=images
```
**Redis
```
REDIS_URL=redis://redis:6379
```
**AWS S3
```
S3_BUCKET_NAME=your-s3-bucket-name
S3_AWS_ACCESS_KEY_ID=your-access-key-id
S3_AWS_SECRET_ACCESS_KEY=your-secret-access-key
```
**Google Drive API
```
GOOGLE_API_KEY=your-google-api-key
```
**Dropbox API
```
DROPBOX_APP_KEY=your-dropbox-app-key
DROPBOX_APP_SECRET=your-dropbox-app-secret
DROPBOX_REFRESH_TOKEN=your-dropbox-refresh-token
```
**Worker Configuration
```
WORKER_COUNT=10
```
5. **Docker Run Command
    ```bash
    docker compose up --build -d
    ```
6.  **Run database migrations:**
    ```bash
    docker compose run --rm api alembic upgrade head
    ```
- The frontend will be accessible at `http://localhost:3000`.
- The API will be accessible at `http://localhost:8000`.

## API Documentation

For detailed API documentation, including request and response formats and `cURL` examples, please see the `API_DOCS.md` file.

## Cloud Deployment

This application is designed to be deployed to any modern cloud platform that supports containers. Here are some potential deployment strategies:

- **Container Orchestration (Kubernetes, ECS):** Deploy the services as containers in a cluster, which provides automated scaling, healing, and load balancing.
- **Serverless (AWS Lambda):** The Import Service could be refactored into a serverless function triggered by a message queue (e.g., SQS), offering a highly scalable and cost-effective solution.
- **PaaS (Heroku, Render):** These platforms can simplify the deployment process by handling the underlying infrastructure.






