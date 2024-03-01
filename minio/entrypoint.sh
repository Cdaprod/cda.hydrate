#!/bin/bash

# Start MinIO in the background
minio server /data --console-address ":9001" &

MINIO_PID=$!

# Function to wait for MinIO to start by checking if `mc` can access it
wait_for_minio() {
    echo "Waiting for MinIO to start..."
    until mc alias set myminio http://localhost:9000 minio minio123 && mc ls myminio; do
        echo "MinIO is unavailable - sleeping"
        sleep 1
    done
}

# Wait for MinIO to become available
wait_for_minio

echo "MinIO is up - setting up buckets..."

# Perform bucket setup
mc mb myminio/weaviate-bucket
mc mb myminio/langchain-bucket
mc mb myminio/cda-datasets
mc mb myminio/python-functions
mc mb myminio/testtesttest

echo "Buckets created."

# Additional setup commands can go here

# Bring MinIO to the foreground
wait $MINIO_PID