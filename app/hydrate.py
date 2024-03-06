from models import MinioClientModel, WeaviateClientModel, URLModel, TextModel, ClientConfig
import requests

def read_urls_from_file(file_path='urls.txt'):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def process_url(url, minio_client, weaviate_client):
    # Example processing logic; you'll need to replace this with your own logic
    response = requests.get(url)
    if response.ok:
        # Assume you have a function to process and store the content
        print(f"Processing {url}")
    else:
        print(f"Failed to fetch {url}")

def main():
    urls = read_urls_from_file('urls.txt')
    
    # Load client configurations (you might want to customize this part based on your actual configuration setup)
    config = ClientConfig(_env_file='.env')
    minio_client = MinioClientModel(config=config).get_client()
    weaviate_client = WeaviateClientModel(config=config).get_client()
    
    for url in urls:
        process_url(url, minio_client, weaviate_client)

if __name__ == "__main__":
    main()
