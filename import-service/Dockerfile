# Use the same Python ECR image as the API service
FROM public.ecr.aws/docker/library/python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the service
CMD ["python", "main.py"]

