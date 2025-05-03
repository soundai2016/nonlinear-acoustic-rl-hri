import os
import numpy as np
from pydub import AudioSegment
import io
import wave
import argparse


def pcm_to_audiosegment(pcm_file, sample_rate=48000, sample_width=2, channels=1):
    with open(pcm_file, 'rb') as pcm:
        pcm_data = pcm.read()
    
    virtual_file = io.BytesIO()
    with wave.open(virtual_file, 'wb') as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm_data)
    
    virtual_file.seek(0)
    
    audio = AudioSegment.from_wav(virtual_file)
    return audio


def calculate_rms(audio):
    return audio.rms

def adjust_power(audio, target_rms):
    current_rms = calculate_rms(audio)
    adjustment_factor = target_rms / current_rms
    return audio.apply_gain(20 * np.log10(adjustment_factor))

def adjust_noise_for_snr(signal, noise, snr_db):
    signal_rms = signal.rms
    noise_rms = noise.rms
    target_noise_rms = signal_rms / (10 ** (snr_db / 20.0))
    adjusted_noise = noise.apply_gain (- 20 * np.log10(noise_rms / target_noise_rms))
    return adjusted_noise

def mix_audio(signal, noise1, noise2, snr_db):

    if len(noise2) < len(noise1):
        noise2 = noise2 * (len(noise1) // len(noise2) + 1)
    noise2 = noise2[:len(noise1)]

    combined_noise = noise1.overlay(noise2)

    adjusted_combined_noise = adjust_noise_for_snr(signal, combined_noise, snr_db)
    
    if len(adjusted_combined_noise) < len(signal):
        adjusted_combined_noise = adjusted_combined_noise * (len(signal) // len(adjusted_combined_noise) + 1)
    adjusted_combined_noise = adjusted_combined_noise[:len(signal)]

    mixed_audio = signal.overlay(adjusted_combined_noise)
    return mixed_audio

def extract_segments(audio, segment_length=60000):
    segments = []
    total_length = len(audio)
    num_segments = total_length // segment_length  

    for i in range(num_segments):
        start_time = i * segment_length
        end_time = start_time + segment_length
        segment = audio[start_time:end_time]
        segments.append(segment)
    return segments

def main():

    parser = argparse.ArgumentParser(description="mix audio file with noise.")
    parser.add_argument("--clean_path", type=str)
    parser.add_argument("--background_noise_path", type=str)
    parser.add_argument("--foreground_noise_path", type=str)
    args = parser.parse_args()

    #input_file
    clean_pcm_path = args.clean_path
    noise1_pcm_path = args.background_noise_path  #background noise, pcm
    noise2_pcm_path = args.foreground_noise_path  #foreground noise, pcm

    clean_audio = pcm_to_audiosegment(clean_pcm_path)
    noise1 = pcm_to_audiosegment(noise1_pcm_path)
    noise2 = pcm_to_audiosegment(noise2_pcm_path)

    min_length = min(len(clean_audio), len(noise1), len(noise2))
    clean_audio = clean_audio[:min_length]
    noise1 = noise1[:min_length]
    noise2 = noise2[:min_length]

    target_rms = calculate_rms(clean_audio)
    noise1 = adjust_power(noise1, target_rms)
    noise2 = adjust_power(noise2, target_rms)

    #snr_levels = [5, 10, 15, 20]
    snr_levels = [-5,-3,0,3,5,10,15,20]

    #output_file
    output_dir = "mix_output"
    os.makedirs(output_dir, exist_ok=True)

    clean_segments = extract_segments(clean_audio, segment_length=60000)

    for snr_db in snr_levels:

        mixed_audio = mix_audio(clean_audio, noise1, noise2, snr_db)

        mixed_segments = extract_segments(mixed_audio, segment_length=60000)

        for i, (mixed_segment, clean_segment) in enumerate(zip(mixed_segments, clean_segments)):
            mixed_output_filename = f"{output_dir}/mixed_{snr_db}dB_segment_{i+1}.wav"
            clean_output_filename = f"{output_dir}/clean_segment_{i+1}.wav"
            mixed_segment.export(mixed_output_filename, format="wav")
            clean_segment.export(clean_output_filename, format="wav")
            print(f"Generated: {mixed_output_filename}")
            print(f"Generated: {clean_output_filename}")

if __name__ == "__main__":
    main()