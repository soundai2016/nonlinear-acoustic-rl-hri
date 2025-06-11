import argparse, requests, time, base64, os, json, re
import logging
from datetime import datetime

BASE_URL = "https://openapi-gateway-azero.soundai.com"
TOKEN = "" # azero api token

def setup_logger():
    """设置日志记录器"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"gasr_result_{current_time}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()

def get_gasr_result(file_path, language, denoise):
    """获取语音识别结果"""
    url = f"{BASE_URL}/asr-one-sentence/v1/transcriptions"
    headers = {
        "Authorization": f"SaiApi {TOKEN}"
    }
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {
            "requestParam": json.dumps({
                "language": language,
                "hotwords": "{}",
                "wav_name": "text",
                "denoise": denoise
            })
        }
        response = requests.post(url, files=files, data=data, headers=headers)
    print(response.text)
    if response.status_code == 200:
        return {
            "result": response.text,
            "language": language
        }
        # result = response.json()
        # if result.get("status") == "completed":
        #     return {
        #         "result": result['response']['text'],
        #         "language": language
        #     }
        # else:
        #     print("Task failed:", result)
        #     return None
    else:
        print("Task submission failed:", response.text)
        return None

def save_output_file(file_base64, output_path):
    """Saves a Base64 encoded file to the specified local path."""
    try:
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(file_base64))
        print(f"Output file saved to: {output_path}")
    except Exception as e:
        print("Failed to save file:", e)

def main():
    parser = argparse.ArgumentParser(description="语音识别转写")
    parser.add_argument("--file_path", type=str, required=True, help="音频文件路径")
    parser.add_argument("--language", type=str, required=True, help="语言类型：auto,zh,en,ja,ko...")   
    args = parser.parse_args()
    
    # 设置日志记录器
    logger = setup_logger()
    
    # 记录开始处理
    logger.info(f"开始处理文件: {args.file_path}, 语言: {args.language}")
    
    result = get_gasr_result(args.file_path, args.language, "1")
    if result:
        # 记录结果
        logger.info(f"转写结果: {json.dumps(result, ensure_ascii=False)}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        logger.error("转写失败")

if __name__ == "__main__":
    main()
