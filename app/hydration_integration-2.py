from pydantic import BaseModel, Field, validator
from typing import List, Optional
import requests
from minio import Minio
import weaviate
import os
import tempfile
import io
import uuid

class ClientConfig(BaseModel):
    minio_endpoint: str = Field(default="play.min.io:9000")
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    weaviate_endpoint: str = Field(default="http://localhost:8080")

class MinioClient(BaseModel):
    config: ClientConfig = Field(default_factory=ClientConfig)

    @property
    def client(self) -> Minio:
        return Minio(
            self.config.minio_endpoint,
            access_key=self.config.minio_access_key,
            secret_key=self.config.minio_secret_key,
            secure=True  # Set to False if you are not using https
        )

class WeaviateClient(BaseModel):
    config: ClientConfig = Field(default_factory=ClientConfig)

    @property
    def client(self) -> weaviate.Client:
        return weaviate.Client(
            url=self.config.weaviate_endpoint,
            timeout_config=(5, 15)
        )

class DataObject(BaseModel):
    content: str
    source_url: Optional[str] = None
    source_file_path: Optional[str] = None
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v

class DataHydrator:
    def __init__(self, minio_client: MinioClient, weaviate_client: WeaviateClient):
        self.minio_client = minio_client
        self.weaviate_client = weaviate_client

    def hydrate_from_url(self, url: str, bucket_name: str) -> Optional[DataObject]:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return None

        file_name = os.path.basename(url)
        file_content = response.content
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_name)

        try:
            with open(file_path, 'wb') as file:
                file.write(file_content)
            self.minio_client.client.fput_object(bucket_name, file_name, file_path)
            print(f"Stored {file_name} in bucket {bucket_name}.")
        except Exception as e:
            print(f"Failed to store {file_name} in Minio: {str(e)}")
            return None

        data_object = DataObject(content=file_content.decode("utf-8"), source_url=url)
        self._index_in_weaviate(data_object)

        return data_object

    def hydrate_from_file(self, file_path: str, bucket_name: str) -> Optional[DataObject]:
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
            file_name = os.path.basename(file_path)
            self.minio_client.client.put_object(bucket_name, file_name, io.BytesIO(file_content), len(file_content))
            print(f"Stored {file_name} in bucket {bucket_name}.")
        except Exception as e:
            print(f"Failed to store {file_name} in Minio: {str(e)}")
            return None

        data_object = DataObject(content=file_content.decode("utf-8"), source_file_path=file_path)
        self._index_in_weaviate(data_object)

        return data_object

    def _index_in_weaviate(self, data_object: DataObject):
        try:
            self.weaviate_client.client.data_object.create(data_object.dict(), "Articles")
            print(f"Indexed content from {data_object.source_url or data_object.source_file_path}.")
        except Exception as e:
            print(f"Failed to index content from {data_object.source_url or data_object.source_file_path} in Weaviate: {str(e)}")

class WeaviateSearcher:
    def __init__(self, weaviate_client: WeaviateClient):
        self.weaviate_client = weaviate_client

    def search(self, query: str) -> List[str]:
        try:
            result = self.weaviate_client.client.query.get("Articles", ["content"]).with_near_text({"concepts": [query]}).do()
            return [article["content"] for article in result["data"]["Get"]["Articles"]]
        except Exception as e:
            print(f"Failed to search in Weaviate: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    config = ClientConfig()
    minio_client = MinioClient(config=config)
    weaviate_client = WeaviateClient(config=config)

    hydrator = DataHydrator(minio_client, weaviate_client)
    searcher = WeaviateSearcher(weaviate_client)

    url = "http://example.com/data"
    bucket_name = "example-bucket"
    hydrator.hydrate_from_url(url, bucket_name)

    file_path = "path/to/local/file.txt"
    hydrator.hydrate_from_file(file_path, bucket_name)

    search_query = "example search query"
    search_results = searcher.search(search_query)
    print(f"Search results for '{search_query}':")
    print("\n".join(search_results))