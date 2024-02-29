import httpx
import pytest

@pytest.mark.asyncio
async def test_process_urls():
    urls = ["https://sanity.cdaprod.dev", "https://blog.min.io/author/david-cannan"]
    async with httpx.AsyncClient() as client:
        # Update the URL to use the service name
        response = await client.post(
            "http://python-app:8000/process-urls/",
            json={"urls": urls}
        )
        assert response.status_code == 200