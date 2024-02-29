import httpx
import pytest

@pytest.mark.asyncio
async def test_process_urls():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/process-urls/",
            json={"urls": ["https://sanity.cdaprod.dev"]}
        )
        assert response.status_code == 200
        assert "URLs processed and stored in MinIO and Weaviate successfully" in response.text
