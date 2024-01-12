# FakeYou StyleTTS 2 Inference

import os
import torch
import argparse
import numpy as np
import soundfile as sf
from styletts2importable import compute_style, inference
from tortoise.utils.text import split_and_recombine_text

def clsynthesize(text_file_path, voice_path, vcsteps, style_npz_path=None, npz_output_path=None):
    # Load the text from the file
    with open(text_file_path, 'r', encoding="utf-8") as file:
        text = file.read()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if style_npz_path and os.path.exists(style_npz_path):
        # Load style vector from NPZ file
        style_vector_np = np.load(style_npz_path)['style_vector']
        custom_voice = torch.from_numpy(style_vector_np).float().to(device)
    elif voice_path:
        # Compute and save style vector
        custom_voice = compute_style(voice_path, save_npz=True, npz_path=npz_output_path or "default_output_path.npz").to(device)
    else:
        raise ValueError("Either a voice path or an input style NPZ file must be provided")

    texts = split_and_recombine_text(text)
    audios = [inference(t, custom_voice, alpha=0.3, beta=0.7, diffusion_steps=vcsteps, embedding_scale=1) for t in texts]

    return 24000, np.concatenate(audios)

def main():
    parser = argparse.ArgumentParser(description='CLI for StyleTTS Voice Synthesis')
    parser.add_argument('--input', type=str, required=True, help='Path to the text file')
    parser.add_argument('--voice', type=str, help='Path to the custom voice audio file (optional if using --input-style-npz)')
    parser.add_argument('--vcsteps', type=int, required=True, help='Number of diffusion steps')
    parser.add_argument('--output', type=str, help='Output path for the synthesized audio file (optional)')
    parser.add_argument('--input-style-npz', type=str, help='Path to the input style vector NPZ file')
    parser.add_argument('--output-style-npz', type=str, help='Output path for the style vector NPZ file')
    args = parser.parse_args()

    if args.output:
        sample_rate, audio = clsynthesize(args.input, args.voice, args.vcsteps, args.input_style_npz, args.output_style_npz)
        sf.write(args.output, audio, sample_rate)

if __name__ == "__main__":
    main()
