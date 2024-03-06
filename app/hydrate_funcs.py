import requests
from minio import Minio
import weaviate
import os
import tempfile
import re
from unstructured.partition.auto import partition
import io

def sanitize_url_to_object_name(url):
    clean_url = re.sub(r'^https?://', '', url)
    clean_url = re.sub(r'[^\w\-_\.]', '_', clean_url)
    return clean_url[:250] + '.txt'

def prepare_text_for_tokenization(text):
    clean_text = re.sub(r'\s+', ' ', text).strip()
    return clean_text

def store_in_minio(url, bucket_name):
    object_name = sanitize_url_to_object_name(url)
    
    # Check if object already exists in MinIO
    exists = minio_client.bucket_exists(bucket_name) and \
             any(obj.object_name == object_name for obj in minio_client.list_objects(bucket_name, prefix=object_name, recursive=True))
    if exists:
        print(f"'{object_name}' already exists in MinIO bucket '{bucket_name}'. Skipping.")
        return False  # Indicates no need to process this URL further

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP issues

        html_content = io.BytesIO(response.content)
        elements = partition(file=html_content, content_type="text/html")
        combined_text = "\n".join([e.text for e in elements if hasattr(e, 'text')])
        combined_text = prepare_text_for_tokenization(combined_text)

        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".txt") as tmp_file:
            tmp_file.write(combined_text)
            tmp_file_path = tmp_file.name
        
        minio_client.fput_object(bucket_name, object_name, tmp_file_path)
        print(f"Stored '{object_name}' in MinIO bucket '{bucket_name}'.")
        os.remove(tmp_file_path)  # Clean up
        return True  # Indicates successful storage and need for further processing
    except requests.RequestException as e:
        print(f"Failed to fetch URL {url}: {e}")
        return False
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return False

def process_documents_in_minio(bucket_name, processed_object_names):
    for object_name in processed_object_names:
        print(f"Processing document: {object_name}")
        file_path = object_name
        minio_client.fget_object(bucket_name, object_name, file_path)

        elements = partition(filename=file_path)
        text_content = "\n".join([e.text for e in elements if hasattr(e, 'text')])

        data_object = {"source": object_name, "content": text_content}
        client.data_object.create(data_object, "Document")
        print(f"Inserted document '{object_name}' into Weaviate.")

        os.remove(file_path)
        print(f"MinIO and Weaviate have ingested '{object_name}'! :)")

#def fetch_and_process_urls(url_list.urls, BUCKET_NAME):
def fetch_and_process_urls(urls, bucket_name, minio_client, weaviate_client):
    processed_object_names = []  # Track successfully processed URLs

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")

    for url in urls:
        if store_in_minio(url, bucket_name):
            processed_object_names.append(sanitize_url_to_object_name(url))
    
    if processed_object_names:
        process_documents_in_minio(bucket_name, processed_object_names)
    else:
        print("No new documents to process.")

# Example usage
# urls = ["https://blog.min.io/author/david-cannan"]
# fetch_and_process_urls(urls, bucket_name)
