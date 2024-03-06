
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import requests
from minio import Minio
import weaviate
import os
import tempfile
import re
from unstructured.partition.auto import partition
import io

class ClientConfig(BaseSettings):
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    weaviate_endpoint: str

    class Config:
        env_file = ".env"

class MinioClientModel(BaseModel):
    config: ClientConfig

    def get_client(self) -> Minio:
        return Minio(
            self.config.minio_endpoint,
            access_key=self.config.minio_access_key,
            secret_key=self.config.minio_secret_key,
            secure=False
        )

    class Config:
        arbitrary_types_allowed = True

class WeaviateClientModel(BaseModel):
    config: ClientConfig

    def get_client(self) -> weaviate.Client:
        return weaviate.Client(self.config.weaviate_endpoint)

    class Config:
        arbitrary_types_allowed = True

class URLModel(BaseModel):
    url: str
    object_name: str = None
    minio_client: Minio

    @validator('url', pre=True)
    def sanitize_url(cls, v: str) -> str:
        return re.sub(r'^https?://', '', v)

    @validator('object_name', pre=True, always=True)
    def set_object_name(cls, v, values):
        url = values.get('url', '')
        clean_url = re.sub(r'[^\w\-_\.]', '_', url)
        return clean_url[:250] + '.txt'

    class Config:
        arbitrary_types_allowed = True

class TextModel(BaseModel):
    text: str
    weaviate_client: weaviate.Client
    source: str

    @validator('text', pre=True)
    def prepare_text(cls, v: str) -> str:
        return re.sub(r'\s+', ' ', v).strip()

    class Config:
        arbitrary_types_allowed = True
