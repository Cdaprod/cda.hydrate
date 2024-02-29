from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
from minio import Minio
import weaviate
import os
import tempfile
import re
from unstructured.partition.auto import partition
import io

app = FastAPI()

# Setup for MinIO and Weaviate
minio_client = Minio("192.168.0.25:9000", access_key="cda_cdaprod", secret_key="cda_cdaprod", secure=False)
weaviate_client = weaviate.Client("http://192.168.0.25:8080")
bucket_name = "cda-datasets"

class URLList(BaseModel):
    urls: List[str]

def sanitize_url_to_object_name(url):
    clean_url = re.sub(r'^https?://', '', url)
    clean_url = re.sub(r'[^\w\-_\.]', '_', clean_url)
    return clean_url[:250] + '.txt'

def prepare_text_for_tokenization(text):
    clean_text = re.sub(r'\s+', ' ', text).strip()
    return clean_text

@app.post("/process-urls/")
async def process_urls(url_list: URLList):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    
    for url in url_list.urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP issues

            html_content = io.BytesIO(response.content)
            elements = partition(file=html_content, content_type="text/html")
            combined_text = "\n".join([e.text for e in elements if hasattr(e, 'text')])
            combined_text = prepare_text_for_tokenization(combined_text)
            object_name = sanitize_url_to_object_name(url)

            with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".txt") as tmp_file:
                tmp_file.write(combined_text)
                tmp_file_path = tmp_file.name
            
            minio_client.fput_object(bucket_name, object_name, tmp_file_path)
            os.remove(tmp_file_path)  # Clean up

            # Now insert into Weaviate
            data_object = {
                "content": combined_text,
                "source": url
            }
            weaviate_client.data_object.create(data_object=data_object, class_name="Document")

        except requests.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL {url}: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing {url}: {e}")

    return {"message": "URLs processed and stored in MinIO and Weaviate successfully"}
    
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)