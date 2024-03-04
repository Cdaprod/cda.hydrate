import requests
import sys
import time

service_url = "http://python-app:8000/health"

timeout = time.time() + 60*1  # 1 minute from now
while True:
    try:
        response = requests.get(service_url)
        if response.status_code == 200:
            print("Service is up and running.")
            sys.exit(0)
    except requests.exceptions.RequestException:
        pass

    if time.time() > timeout:
        print("Timed out waiting for the service to be ready.")
        sys.exit(1)

    time.sleep(5)