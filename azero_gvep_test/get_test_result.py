import os
import numpy as np
from pydub import AudioSegment
from pesq import pesq
import math
import argparse

def calculate_mos_lqo(pesq_score):
    # 非线性公式，根据实际情况调整
    mos_lqo=0.999 + (4.999 - 0.999) / (1 + math.exp(-1.4945 * pesq_score + 4.6607))
    #mos_lqo = 1.0 + 0.035 * pesq_score + pesq_score ** 2 / 100
    return mos_lqo

def get_audio_data(file_path):
    # 读取音频文件并转换为16kHz单声道
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    return np.array(audio.get_array_of_samples())

def main(gvep_path, answer_path, output_file):
    # 检查文件是否存在
    if not os.path.exists(gvep_path) or not os.path.exists(answer_path):
        print("Error: One or both input files do not exist")
        return

    # 获取音频数据
    clean_data = get_audio_data(gvep_path)
    mixed_data = get_audio_data(answer_path)

    # 确保两个音频文件的长度一致
    min_length = min(len(clean_data), len(mixed_data))
    clean_data = clean_data[:min_length]
    mixed_data = mixed_data[:min_length]

    # 计算PESQ值
    pesq_score = pesq(16000, clean_data, mixed_data, 'wb')
    # 计算MOS-LQO值
    mos_lqo_score = calculate_mos_lqo(pesq_score)

    # 将结果写入文本文件
    with open(output_file, 'w') as f:
        f.write("File\tPESQ Score\tMOS-LQO Score\n")
        f.write(f"{os.path.basename(gvep_path)}\t{pesq_score:.4f}\t{mos_lqo_score:.4f}\n")

    print(f"Results saved to {output_file}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Get test result.")
    parser.add_argument("--answer_path", type=str, help="Path to the clean file.")
    parser.add_argument("--gvep_path", type=str, help="Path to the gVEP output file.")
    parser.add_argument("--output_file", type=str, help="Path to get the output result.")
    args = parser.parse_args()

    answer_path = args.answer_path
    gvep_path = args.gvep_path
    output_file=args.output_file
    main(gvep_path, answer_path, output_file)