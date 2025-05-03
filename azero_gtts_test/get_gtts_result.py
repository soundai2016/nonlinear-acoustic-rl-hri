import requests
import argparse
import json
import os
from pathlib import Path
import time
import librosa


BASE_URL = "https://openapi-gateway-azero.soundai.com"
TOKEN = "" # azero api token
VERIFY_SSL = False  # Set to False if using self-signed certificates

def get_audio_duration_librosa(file_path):
    audio, sr = librosa.load(file_path, sr=None)
    duration = librosa.get_duration(y=audio, sr=sr)
    return duration


def clone_voice(file_path, speaker_name, language, emotion = "default", enable_asr = "True"):
    url = f"{BASE_URL}/ntts-clone/v3/clone"
    headers = {
        "Authorization": f"SaiApi {TOKEN}"
    }
    with open(file_path, "rb") as f:
        files = {"wav_file": (os.path.basename(file_path), f, "audio/wav")}
        data = {
            "speaker_name": speaker_name,
            "emotion": emotion,
            "enable_asr": enable_asr,
            "language": language
        }
        print(f"Uploading file: {file_path}")
        response = requests.post(url, files=files, data=data, headers=headers, verify=VERIFY_SSL)
    if response.status_code == 200:
        result = response.json()
        print(result)
    else:
        print("Task submission failed:", response.text)

def query_character_name(speaker_name="20250416000002_test_en_123456"):
    url = f"{BASE_URL}/ntts-clone/v3/query"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"SaiApi {TOKEN}"
    }
    data = {
        "speaker_name": speaker_name
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        success = result.get("success", False)
        print(f"Success: {success}")
        return success # 返回 success 和完整结果
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return False

def generate_tts_voice(
    server_url: str = f"{BASE_URL}/ntts-clone/v3/speech",
    output_path: str = "test/out_audio/tts_curl_py.mp3",
    **kwargs
) -> bool:
    default_params = {
        # "speaker_name": "20250223182728_xiaoxiong_zh_123456",
        "speaker_name": "20250415145558_qbnjfy_zh_573274",
        "text": "Hello SoundAI, 我是声智科技的测试员, My name is 小易。声智科技を愛しています",
        "language": "auto",
        "emotion": "default",
        "batch_size": 10,
        "speed": 1.0,
        "top_k": 3,
        "top_p": 0.8,
        "temperature": 0.8,
        "stream": False,
        "format": "wav",
        "save_temp": False
    }

    params = {**default_params, **kwargs}
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SaiApi {TOKEN}"
        }

        response = requests.post(
            url=server_url,
            headers=headers,
            data=json.dumps(params),
            stream=True
        )
        response.raise_for_status()  # 检查HTTP错误

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"语音生成成功，保存至: {os.path.abspath(output_path)}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"服务器返回: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload and process an audio file.")
    parser.add_argument("--file-path", type=str)
    parser.add_argument("--speaker_name", type=str)
    parser.add_argument("--text", type=str)
    args = parser.parse_args()
    
    file_path = args.file_path
    output_path = "output/test.wav"
    speaker_name = args.speaker_name
    text = args.text

    clone_voice(
       file_path = file_path,
        language = "en",
        speaker_name = speaker_name
    )
    while True:
        result = query_character_name(
            speaker_name = speaker_name
            # speaker_name = "20250416000008_test_en_123450",
        )
        if(result == True):
            print(result)
            break
        else:
            print(result)
    start_time = time.time()  # 记录开始时间
    generate_tts_voice(
        output_path = output_path,
        speaker_name = speaker_name,
        text = text,
        format="wav",
        speed=1
    )
    end_time = time.time()  # 记录结束时间
    execution_time = end_time - start_time  # 计算执行时间（秒）
    duration = get_audio_duration_librosa(output_path)
    print(f"执行时间: {execution_time:.4f} 秒")
    print(f"音频时长: {duration:.4f} 秒")
    print(f"RTF: {execution_time/duration:.4f}")
    
    