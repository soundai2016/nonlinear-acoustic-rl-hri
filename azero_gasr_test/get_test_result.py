import re
from jiwer import wer
import string
import jieba
import argparse
import json
import os

def compute_wer_by_single(reference_text: str, hypothesis_text: str):
    hypothesis_clean = re.sub(r'[^\w\s]', '', hypothesis_text.strip())
    hypothesis_clean = hypothesis_clean.replace(" ", "") 
    hypothesis_clean = ' '.join(hypothesis_clean)
    reference_text = re.sub(r'[^\w\s]', '', reference_text.strip())
    reference_text = reference_text.replace(" ", "") 
    reference_text = ' '.join(reference_text)
    # print(reference_text)
    # print(hypothesis_clean)
    # 计算 WER
    wer_score = wer(reference_text, hypothesis_clean)
    return wer_score

def process_file(log_file: str, reference_file: str):
    # 提取识别结果
    asr_results = {}  # key: file_id, value: predicted_text
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        current_file = None
        for line in lines:
            # 匹配文件路径行
            file_match = re.search(r"开始处理文件: (.*?), 语言:", line)
            if file_match:
                current_file = file_match.group(1)
            # 匹配转写结果行
            trans_match = re.search(r"转写结果: (.*)", line)
            if trans_match and current_file:
                try:
                    result = json.loads(trans_match.group(1))
                    text = result.get('result', '').strip()
                    if text:
                        file_id = os.path.basename(current_file)
                        asr_results[file_id] = text
                except json.JSONDecodeError:
                    continue

    print(f"Processing reference file: {reference_file}")
    reference_dict = {}  # key: file_id, value: reference_text
    with open(reference_file, "r", encoding="utf-8") as f: 
        for line in f:
            parts = line.strip().split("\t")  # 用tab分隔
            if len(parts) >= 2:
                file_id = parts[1]
                text = parts[2]  # 把参考文本拼接起来
                reference_dict[file_id] = text
    
    total_wer = 0
    count = 0
    for file_id, hyp in asr_results.items():
        if file_id in reference_dict:
            ref = reference_dict[file_id]
            wer_score = compute_wer_by_single(ref, hyp)
            total_wer += wer_score
            count += 1
    
    if count > 0:
        print(f"Average WER over {count} samples: {total_wer / count:.2%}\n")
    else:
        print("No matching entries found.")

def main():
    parser = argparse.ArgumentParser(description='Calculate WER for ASR results')
    parser.add_argument('log_file', help='Path to the log file containing ASR results')
    parser.add_argument('reference_file', help='Path to the reference file (TSV format)')
    
    args = parser.parse_args()
    process_file(args.log_file, args.reference_file)

if __name__ == "__main__":
    main()
