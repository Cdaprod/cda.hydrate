#!/bin/bash

# Start MinIO in the background
minio server /data --console-address ":9001" &

MINIO_PID=$!

# Wait for MinIO to start
echo "Waiting for MinIO to start..."
until curl -s http://localhost:9000/minio/health/live; do
  sleep 1
done

# Perform bucket setup
mc alias set myminio http://localhost:9000 minio minio123
mc mb myminio/weaviate-bucket
mc mb myminio/langchain-bucket

# Additional setup commands can go here

# Bring MinIO to the foreground
wait $MINIO_PID