#!/bin/bash

# Function to check if Weaviate is up
wait_for_weaviate() {
    echo "Waiting for Weaviate to be available..."
    until python -c "import requests; requests.get('http://weaviate:8080/v1/.well-known/ready')" &> /dev/null
    do
        echo "Weaviate is unavailable - sleeping"
        sleep 1
    done
}

# Wait for Weaviate to become available
wait_for_weaviate

echo "Weaviate is up - executing command"
# Start the FastAPI app using Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload