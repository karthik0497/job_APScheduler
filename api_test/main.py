# api_test.py

import time
import requests
import os
import urllib3
urllib3.disable_warnings()

# Load environment variables
# BASE_URL = os.getenv("HOST_URL")
BASE_URL = os.getenv("BASE_URL")
API_KEY_NAME = os.getenv('API_KEY_NAME')
API_KEY = os.getenv('API_KEY')
API_ACCESS_TOKEN = os.getenv('API_ACCESS_TOKEN', '123456')

# Verify that environment variables are loaded correctly
if not BASE_URL or not API_KEY_NAME or not API_KEY:
    raise EnvironmentError("Missing environment variables for API base URL or keys")

# Headers
headers_dict = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_ACCESS_TOKEN}',
    API_KEY_NAME: API_KEY
}

# Debug print to ensure headers_dict is correctly set
print(f"Headers: {headers_dict}")
def call_rest_api(request_type, endpoint, data=None, params=None, no_token=False, num_tries=10):
    REQUESTS_TIMEOUT = 60
    for i in range(num_tries):
        try:
            url = endpoint
            if request_type == "get":
                if no_token:
                    response = requests.get(url, params=params, timeout=REQUESTS_TIMEOUT)
                else:
                    response = requests.get(url, params=params, timeout=REQUESTS_TIMEOUT, headers=headers_dict)
            elif request_type == "post":
                response = requests.post(url, json=data, params=params, timeout=REQUESTS_TIMEOUT, headers=headers_dict)
            elif request_type == "patch":
                response = requests.patch(url, json=data, params=params, timeout=REQUESTS_TIMEOUT, headers=headers_dict)
            elif request_type == "delete":
                response = requests.delete(url, params=params, timeout=REQUESTS_TIMEOUT, headers=headers_dict)
                return response.json()  # Return JSON directly if deleting
            else:
                print("call_rest_api - ERROR - unknown request_type")
                return {"status": "failure", "statusbool": False}

            print("Raw response content:", response.content)  # Print raw response content for debugging

            try:
                return response.json()
            except ValueError:
                print("Response is not in JSON format")
                return {"status": "failure", "statusbool": False}

        except requests.RequestException as e:
            print("Internet Connection error occurred, retrying ....", e)
            time.sleep(3)

    return {"status": "failure", "statusbool": False}

def test_getall_job():
    start_time = time.time()
    response = call_rest_api("get", f"{BASE_URL}/jobs")
    total_time = time.time() - start_time
    print(f"Get Job - Time: {total_time:.2f}s, Data: {response}")

def test_get_job(job_id):
    start_time = time.time()
    response = call_rest_api("get", f"{BASE_URL}/jobs/{job_id}")
    total_time = time.time() - start_time
    print(f"Get Job - Time: {total_time:.2f}s, Data: {response}")

def test_create_job():
    job_data = {
        "job_name": "Test Job",
        "job_schedule": "22:30 thursday may 30",
        "job_description": "A test job",
        "job_type": "test",
        "job_params": {"param1": "value1"}
    }
    start_time = time.time()
    response = call_rest_api("post", f"{BASE_URL}/jobs", data=job_data)
    total_time = time.time() - start_time
    print(f"Create Job - Time: {total_time:.2f}s, Data: {response}")
    return response.get("job_id") if isinstance(response, dict) else None

def test_delete_all_jobs():
    start_time = time.time()
    response = call_rest_api("delete", f"{BASE_URL}/jobs")
    total_time = time.time() - start_time
    print(f"Delete All Jobs - Time: {total_time:.2f}s, Data: {response}")

def test_delete_job(job_id):
    start_time = time.time()
    response = call_rest_api("delete", f"{BASE_URL}/jobs/{job_id}")
    total_time = time.time() - start_time
    print(f"Delete Job - Time: {total_time:.2f}s, Data: {response}")



def run_tests():
    test_getall_job()
    job_id = test_create_job()
    if job_id:
        test_get_job(job_id)
        test_delete_job(job_id)
    test_delete_all_jobs()

if __name__ == "__main__":
    run_tests()
