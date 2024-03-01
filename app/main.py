from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from hydrate_funcs import fetch_and_process_urls  # Adjusted import statement
from minio import Minio
import weaviate
from dotenv import load_dotenv
import os

app = FastAPI()

# Manually specify the path if running outside Docker
load_dotenv(dotenv_path=".env.local")

# Now access your environment variables
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
USE_SSL = os.getenv("USE_SSL", "false").lower() in ['true', '1', 't']
WEAVIATE_ENDPOINT = os.getenv("WEAVIATE_ENDPOINT", "http://weaviate:8080")
BUCKET_NAME = os.getenv("BUCKET_NAME", "cda-datasets")

# Setup for MinIO and Weaviate
minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=USE_SSL)
weaviate_client = weaviate.Client(WEAVIATE_ENDPOINT)

class URLList(BaseModel):
    urls: List[str]

@app.post("/process-urls/")
async def process_urls(url_list: URLList):
    # Utilize the imported function to process URLs
    try:
        fetch_and_process_urls(url_list.urls, bucket_name, minio_client, weaviate_client)
        return {"message": "URLs processed and stored in MinIO and Weaviate successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
