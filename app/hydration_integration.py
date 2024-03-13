from pydantic import BaseModel
import requests
from minio import Minio
import weaviate
import os
import tempfile
import io

class ClientConfig(BaseModel):
    minio_endpoint: str = "play.min.io:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    weaviate_endpoint: str = "http://localhost:8080"

class MinioClientModel(BaseModel):
    config: ClientConfig

    def get_client(self) -> Minio:
        return Minio(
            self.config.minio_endpoint,
            access_key=self.config.minio_access_key,
            secret_key=self.config.minio_secret_key,
            secure=True  # Set to False if you are not using https
        )

class WeaviateClientModel(BaseModel):
    config: ClientConfig

    def get_client(self) -> weaviate.Client:
        return weaviate.Client(
            url=self.config.weaviate_endpoint,
            timeout_config=(5, 15)
        )

def hydrate_data(url: str, bucket_name: str, config: ClientConfig):
    minio_client = MinioClientModel(config=config).get_client()
    weaviate_client = WeaviateClientModel(config=config).get_client()

    # Fetch the data
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return

    # Store in Minio
    file_name = os.path.basename(url)
    file_content = response.content
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, file_name)

    with open(file_path, 'wb') as file:
        file.write(file_content)
    
    try:
        minio_client.fput_object(bucket_name, file_name, file_path)
        print(f"Stored {file_name} in bucket {bucket_name}.")
    except Exception as e:
        print(f"Failed to store {file_name} in Minio: {str(e)}")
        return

    # Index in Weaviate
    data_object = {
        "content": file_content.decode("utf-8"),  # Assuming the content is text
        "sourceUrl": url
    }
    try:
        weaviate_client.data_object.create(data_object, "Articles")
        print(f"Indexed content from {url}.")
    except Exception as e:
        print(f"Failed to index content from {url} in Weaviate: {str(e)}")

# Example usage
if __name__ == "__main__":
    config = ClientConfig()
    url = "http://example.com/data"
    bucket_name = "example-bucket"
    hydrate_data(url, bucket_name, config)
