import requests
import os

API_URL = 'https://digitalbrain.techschool.lu/artifacts/'

def upload_artifacts(uuid):
    print('upload_artifacts start')

    api_url = f"{API_URL}{uuid}"
    directory = "artifacts"
    allowed_extensions = {".mp4", ".mid"}

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if os.path.isfile(file_path) and any(filename.endswith(ext) for ext in allowed_extensions):
            with open(file_path, "rb") as file:
                files = {"file": file}
                response = requests.post(api_url, files=files)
                
                # Check response content before parsing JSON
                try:
                    json_response = response.json()
                except requests.exceptions.JSONDecodeError:
                    json_response = {"error": "Invalid or empty response from server", "status_code": response.status_code}

                print(f"... uploading {filename}: {response.status_code} - {json_response}")

    print('upload_artifacts end')
