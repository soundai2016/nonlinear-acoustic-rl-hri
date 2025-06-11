import argparse
import requests
import time
import base64
import os
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Server address (note: use verify=False when using self-signed certificates)
BASE_URL = "https://openapi-gateway-azero.soundai.com"
TOKEN = "" # azero api token

VERIFY_SSL = False  # Set to False if using self-signed certificates

def upload_audio_file(file_path, trim_duration):
    """
    Uploads an audio file by calling the denoise endpoint with trim duration and returns the task id.
    """
    url = f"{BASE_URL}/denoise/v1/filter"
    headers = {
        "Authorization": f"SaiApi {TOKEN}"
    }
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "audio/wav")}
        data = {"trim_duration": str(trim_duration)}  # Ensure trim_duration is sent as a string
        print(f"Uploading file: {file_path} with trim duration: {trim_duration} seconds")
        response = requests.post(url, files=files, data=data, verify=VERIFY_SSL, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print("result: ", result)
        taskid = result.get("data")
        data = json.loads(taskid)
        taskid = data["taskid"]
        print(f"Task submitted, taskid: {taskid}")
        return taskid
    else:
        print("Task submission failed:", response.text)
        return None

def query_task_status(taskid):
    """
    Polls the task status and returns the complete JSON data from the endpoint.
    """
    url = f"{BASE_URL}/denoise/v1/task"
    headers = {
        # "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"SaiApi {TOKEN}"
    }
    params = {"id": taskid}
    response = requests.post(url, params=params, verify=VERIFY_SSL, headers=headers)
    # response = requests.get(url, verify=VERIFY_SSL, headers=headers)
    print("response: ", response)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to query task status:", response.text)
        return None

def save_output_file(file_bytes, output_path):
    """
    Saves the Base64 encoded file data to a local file.
    """
    try:
        # file_bytes = base64.b64decode(file_base64)
        with open(output_path, "wb") as f:
            f.write(file_bytes)
        print(f"Denoised file saved to: {output_path}")
    except Exception as e:
        print("Failed to save file:", e)

def main():
    # # Parse command line arguments for input, output file paths, and trim duration
    parser = argparse.ArgumentParser(description="Upload and process an audio file for denoising.")
    parser.add_argument("--input_file", type=str, default="test_demo/music.mp3", help="Path to the input audio file.")
    parser.add_argument("--trim_duration", type=int, default=600, help="Trim duration in seconds (60-7200). Default is 600 seconds.")
    parser.add_argument("--output_file", type=str, default="gvep_demo/test.mp3", help="Path to the output audio file.")
    args = parser.parse_args()
    
    input_file = args.input_file
    trim_duration = args.trim_duration
    output_file = args.output_file

    # Validate trim duration
    if trim_duration < 60 or trim_duration > 7200:
        print("Error: Trim duration must be between 60 and 7200 seconds.")
        return

    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist, please check the path!")
        return
    
    if not os.path.exists(output_file):
        print(f"File {output_file} does not exist, please check the path!")
        return

    # Upload the audio file and obtain the task id
    taskid = upload_audio_file(input_file, trim_duration)
    if not taskid:
        return
    # Poll the task status
    print("taskid = {}", taskid)
    print("Starting to poll task status...")
    
    while True:
        status_info = query_task_status(taskid)
        if status_info is not None:
            save_output_file(status_info, output_file)
            break

if __name__ == "__main__":
    main()