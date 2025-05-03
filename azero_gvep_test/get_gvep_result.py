import argparse
import requests
import time
import base64
import os
import urllib3

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
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"trim_duration": str(trim_duration)}  # Ensure trim_duration is sent as a string
        print(f"Uploading file: {file_path} with trim duration: {trim_duration} seconds")
        response = requests.post(url, files=files, data=data, verify=VERIFY_SSL)
    if response.status_code == 200:
        result = response.json()
        taskid = result.get("taskid")
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
    params = {"taskid": taskid}
    response = requests.post(url, params=params, verify=VERIFY_SSL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to query task status:", response.text)
        return None

def save_output_file(file_base64, output_path):
    """
    Saves the Base64 encoded file data to a local file.
    """
    try:
        file_bytes = base64.b64decode(file_base64)
        with open(output_path, "wb") as f:
            f.write(file_bytes)
        print(f"Denoised file saved to: {output_path}")
    except Exception as e:
        print("Failed to save file:", e)

def main():
    # Parse command line arguments for input, output file paths, and trim duration
    parser = argparse.ArgumentParser(description="Upload and process an audio file for denoising.")
    parser.add_argument("--input", type=str, default="test/music.wav", help="Path to the input audio file.")
    parser.add_argument("--trim_duration", type=int, default=600, help="Trim duration in seconds (60-7200). Default is 600 seconds.")
    args = parser.parse_args()
    
    input_file = args.input
    output_file = "gvep_output/test.mp3"
    trim_duration = args.trim_duration

    # Validate trim duration
    if trim_duration < 60 or trim_duration > 7200:
        print("Error: Trim duration must be between 60 and 7200 seconds.")
        return

    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist, please check the path!")
        return

    # Upload the audio file and obtain the task id
    taskid = upload_audio_file(input_file, trim_duration)
    if not taskid:
        return

    # Poll the task status
    print("Starting to poll task status...")
    while True:
        status_info = query_task_status(taskid)
        if not status_info:
            break
        
        status = status_info.get("status")
        print(f"Current task status: {status}")
        
        # If available, print processing time and audio length
        processing_time = status_info.get("processing_time")
        audio_length = status_info.get("audio_length")
        if processing_time is not None:
            print(f"Processing time: {processing_time:.2f} seconds")
        if audio_length is not None:
            print(f"Audio length: {audio_length:.2f} seconds")

        if status == "completed":
            file_base64 = status_info.get("file_base64")
            if file_base64:
                save_output_file(file_base64, output_file)
            else:
                print("Task completed, but no file data was returned.")
            break
        elif status == "failed":
            print("Task processing failed. Error message:", status_info.get("error"))
            break
        else:
            # Task is still processing; wait before polling again
            time.sleep(5)

if __name__ == "__main__":
    main()