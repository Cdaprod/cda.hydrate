

import httpx
import pytest

@pytest.mark.asyncio
async def test_process_urls():
    urls = ["https://sanity.cdaprod.dev", "https://blog.min.io/author/david-cannan"]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/process-urls/",
            json={"urls": urls}
        )
        assert response.status_code == 200 
        assert "Hydrated services with URLs, processed and stored in MinIO and Weaviate successfully" in response.text