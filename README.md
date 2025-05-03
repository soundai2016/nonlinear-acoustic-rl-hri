# Azero Acoustic Model Testing Scripts

This repository contains scripts and instructions for testing Azero acoustic models, including AzeroVEP, AzeroTTS, and AzeroASR. The experimental environment, datasets, and evaluation methods are detailed below and align with the reproducibility guidelines provided in the appendix of our research paper.


---------
## [1] azero-gvep-test - azerovep model test scripts
---------
### mix_with_noise.py
+ desc: Mixes a speech file with background and foreground noise to generate a synthesized audio file.
+ run example：python mix_noise.py \
        --clean_path xxx \
        --background_noise_path xxx \
        --foreground_noise_path xxx

### get_gvep_result.py
+ desc: Invokes the Azero GVEP model API to process audio files and returns the enhanced output results.
+ run example: python get_gvep_result.py 
        --input_path xxx \
        --trim_duration 600 \
+ to get api token, visit: https://azero.soundai.com/#/voice?id=denoise

### get_test_result.py
+ desc: Analyzes and compares the GVEP model output with reference files to generate test evaluation results.
+ run example: python get_test_result.py --gvep_path xxx --answer_path xxx

---------
## [2] azero-gtts-test - azerotts model test scripts
---------
### get_gtts_result.py
+ desc: Invokes the Azero GTTS model API to convert text into speech with specified speaker voice.
+ run example：python test_gtts_api.py \
        --file_path xxx \
        --speaker_name "20250416000002_test_en_123456" \
        --text "A cold, bright moon was shining with clear sharp lights and shadows."
+ to get api token, visit: https://azero.soundai.com/#/voice?id=ntts_clone

### get test results via github repos blow:
+ MOS calculation  https://github.com/gabrielmittag/NISQA
+ SIM-O calculation  https://github.com/microsoft/UniSpeech
+ WER calculation https://github.com/facebookresearch/fairseq/tree/main/examples/hubert

---------
## [3] azero-gasr-test - azeroasr model test scripts
---------
### get_gasr_result.py
+ desc: Invokes the Azero GASR model API to perform speech recognition and convert speech into text.
+ run example：python get_gasr_result.py --file_path xxx
+ to get api token, visit: https://azero.soundai.com/#/voice?id=asr_one_sentence

### get_test_result.py
+ desc: Analyzes the GASR model output logs to generate test evaluation results and performance metrics.
+ run example：python get_test_result.py --log_path xxx --language zh

## [4] Evaluation Methods
+ MOS Calculation: [NISQA GitHub Repository](https://github.com/gabrielmittag/NISQA)
+ SIM-O Calculation: [UniSpeech GitHub Repository](https://github.com/microsoft/UniSpeech)
+ WER Calculation: [HuBERT GitHub Repository](https://github.com/microsoft/UniSpeech)

## [5] Evaluation Dataset

- **LibriSpeech**: A 1,000-hour corpus of 16 kHz English read speech from audiobooks.  
  Download: [OpenSLR SLR12](https://www.openslr.org/12) :contentReference[oaicite:0]{index=0}

- **AISHELL-1**: A 170-hour Mandarin speech corpus (400 speakers, 16 kHz) for ASR research.  
  Download: [OpenSLR SLR33](https://www.openslr.org/33) :contentReference[oaicite:1]{index=1}

- **AISHELL-2**: A 1,000-hour clean read-speech Mandarin dataset for industrial-scale ASR.  
  Download: [AISHELL-2 official site](http://www.aishelltech.com/aishell_2) :contentReference[oaicite:2]{index=2}

- **FLEURS**: An n-way parallel speech dataset in 102 languages (~12 h per language) for multilingual ASR and evaluation.  
  Download: [google/fleurs on Hugging Face](https://huggingface.co/datasets/google/fleurs) :contentReference[oaicite:3]{index=3}

- **Common Voice**: A massive, community-contributed multilingual speech dataset with validated recordings.  
  Download: [Mozilla Common Voice datasets](https://commonvoice.mozilla.org/datasets) :contentReference[oaicite:4]{index=4}
