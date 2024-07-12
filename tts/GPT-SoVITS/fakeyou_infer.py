import sys
import os

# Add current working directory and specific subdirectories to sys.path
now_dir = os.getcwd()
sys.path.insert(0, now_dir)
sys.path.insert(0, os.path.join(now_dir, "tools"))
sys.path.insert(0, os.path.join(now_dir, "tools/damo_asr"))
sys.path.insert(0, os.path.join(now_dir, "GPT_SoVITS"))
sys.path.insert(0, os.path.join(now_dir, "tools/uvr5"))

print("Current working directory:", os.getcwd())
print("Python sys.path:", sys.path)

import argparse
import traceback
import random
import torch
import numpy as np
import soundfile as sf
import yaml
from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config
from GPT_SoVITS.TTS_infer_pack.text_segmentation_method import get_method_names as get_cut_method_names

# Print environment variables
print("Env vars:")
print(os.environ)

def print_gpu_info():
    print('========================================')
    print('Python interpreter:', sys.executable)
    print('PyTorch version:', torch.__version__)
    print('CUDA Available?', torch.cuda.is_available())
    print('CUDA Device count:', torch.cuda.device_count())
    print('CUDA architectures library was compiled for:', torch.cuda.get_arch_list())
    print('========================================', flush=True)

print_gpu_info()

cut_method_names = get_cut_method_names()

def load_yaml_config(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    return config_data

def create_tts_config(config_path):
    config_data = load_yaml_config(config_path)
    config = config_data.get('custom', config_data.get('default', {}))

    tts_config = TTS_Config(config)
    tts_config.device = config.get('device', 'cpu')
    tts_config.is_half = config.get('is_half', False)

    return tts_config

def print_tts_config(config):
    print("---------------------------------------------TTS Config---------------------------------------------")
    print(f"device              : {config.device}")
    print(f"is_half             : {config.is_half}")
    print(f"t2s_weights_path    : {config.t2s_weights_path}")
    print(f"vits_weights_path   : {config.vits_weights_path}")
    print(f"bert_base_path      : {config.bert_base_path}")
    print(f"cnhuhbert_base_path : {config.cnhuhbert_base_path}")
    print("----------------------------------------------------------------------------------------------------")

def inference(config, text, text_lang, ref_audio_path, prompt_text, prompt_lang, top_k, top_p, temperature, text_split_method, batch_size, speed_factor, ref_text_free, split_bucket, fragment_interval, seed, keep_random, parallel_infer, repetition_penalty, output_path):
    seed = -1 if keep_random else seed
    actual_seed = seed if seed not in [-1, "", None] else random.randrange(1 << 32)
    inputs = {
        "text": text,
        "text_lang": text_lang,
        "ref_audio_path": ref_audio_path,
        "prompt_text": prompt_text if not ref_text_free else "",
        "prompt_lang": prompt_lang,
        "top_k": top_k,
        "top_p": top_p,
        "temperature": temperature,
        "text_split_method": text_split_method,
        "batch_size": int(batch_size),
        "speed_factor": float(speed_factor),
        "split_bucket": split_bucket,
        "return_fragment": False,
        "fragment_interval": fragment_interval,
        "seed": actual_seed,
        "parallel_infer": parallel_infer,
        "repetition_penalty": repetition_penalty,
    }
    
    tts_pipeline = TTS(config)
    
    print(f"Using Text2Semantic model: {config.t2s_weights_path}")
    print(f"Using VITS model: {config.vits_weights_path}")

    for item in tts_pipeline.run(inputs):
        audio_data = item[1]  # assuming item[1] is the audio data
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_file = os.path.join(output_path, f"output_{actual_seed}.wav")
        sf.write(output_file, audio_data, 32000, subtype='PCM_16')
        print(f"Output saved to {output_file}, Seed: {actual_seed}")

def main():
    parser = argparse.ArgumentParser(description="Inference CLI for GPT-SoVITS")
    parser.add_argument('--config', type=str, default='GPT_SoVITS/configs/tts_infer.yaml', help='Path to the configuration file')
    parser.add_argument('--gpt_model', type=str, help='Path to the GPT model')
    parser.add_argument('--sovits_model', type=str, help='Path to the SoVITS model')
    parser.add_argument('--ref_audio', type=str, required=True, help='Path to the reference audio file')
    parser.add_argument('--ref_text', type=str, required=True, help='Path to the reference text file')
    parser.add_argument('--target_language', type=str, required=True, choices=["zh", "en", "ja", "zh_en", "ja_en", "multi"], help='Target language for synthesis')
    parser.add_argument('--ref_language', type=str, required=True, choices=["zh", "en", "ja", "zh_en", "ja_en", "multi"], help='Reference language')
    parser.add_argument('--target_text', type=str, required=True, help='Path to the target text file')
    parser.add_argument('--how_to_cut', type=str, required=True, choices=["cut0", "cut1", "cut2", "cut3", "cut4", "cut5"], help='Text split method')
    parser.add_argument('--output_path', type=str, required=True, help='Path to save the output')
    parser.add_argument('--top_k', type=int, default=5, help='Top k sampling')
    parser.add_argument('--top_p', type=float, default=1.0, help='Top p sampling')
    parser.add_argument('--temperature', type=float, default=1.0, help='Temperature for sampling')
    parser.add_argument('--batch_size', type=int, default=20, help='Batch size for inference')
    parser.add_argument('--speed_factor', type=float, default=1.0, help='Speed factor for synthesis')
    parser.add_argument('--split_bucket', action='store_true', help='Enable data bucketing')
    parser.add_argument('--fragment_interval', type=float, default=0.3, help='Interval between audio fragments')
    parser.add_argument('--seed', type=int, default=-1, help='Random seed')
    parser.add_argument('--keep_random', action='store_true', help='Keep random seed')
    parser.add_argument('--parallel_infer', action='store_true', help='Enable parallel inference')
    parser.add_argument('--repetition_penalty', type=float, default=1.35, help='Repetition penalty for T2S model')
    
    args = parser.parse_args()

    # Create TTS configuration
    tts_config = create_tts_config(args.config)

    # Override model paths if provided
    if args.gpt_model:
        tts_config.t2s_weights_path = args.gpt_model
    if args.sovits_model:
        tts_config.vits_weights_path = args.sovits_model

    # Print the TTS configuration
    print_tts_config(tts_config)

    # Read input files
    with open(args.ref_text, 'r', encoding='utf-8') as f:
        prompt_text = f.read().strip()
    with open(args.target_text, 'r', encoding='utf-8') as f:
        target_text = f.read().strip()

    # Call the inference function
    inference(
        tts_config,
        text=target_text,
        text_lang=args.target_language,
        ref_audio_path=args.ref_audio,
        prompt_text=prompt_text,
        prompt_lang=args.ref_language,
        top_k=args.top_k,
        top_p=args.top_p,
        temperature=args.temperature,
        text_split_method=args.how_to_cut,
        batch_size=args.batch_size,
        speed_factor=args.speed_factor,
        ref_text_free=False,
        split_bucket=args.split_bucket,
        fragment_interval=args.fragment_interval,
        seed=args.seed,
        keep_random=args.keep_random,
        parallel_infer=args.parallel_infer,
        repetition_penalty=args.repetition_penalty,
        output_path=args.output_path
    )

if __name__ == "__main__":
    main()
