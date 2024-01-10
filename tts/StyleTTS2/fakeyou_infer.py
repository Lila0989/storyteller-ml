# FakeYou StyleTTS 2 Inference

import argparse
import numpy as np
import soundfile as sf
from styletts2importable import compute_style, inference
from tortoise.utils.text import split_and_recombine_text

def clsynthesize(text, voice_path, vcsteps):
    # Load the custom voice
    custom_voice = compute_style(voice_path)

    # Split and recombine long text into manageable chunks
    texts = split_and_recombine_text(text)

    audios = []
    for t in texts:
        # Generate audio for each text chunk
        audios.append(inference(t, custom_voice, alpha=0.3, beta=0.7, diffusion_steps=vcsteps, embedding_scale=1))

    return 24000, np.concatenate(audios)

def main():
    parser = argparse.ArgumentParser(description='CLI for StyleTTS Voice Synthesis')
    parser.add_argument('--text', type=str, required=True, help='Text to synthesize')
    parser.add_argument('--voice', type=str, required=True, help='Path to the custom voice audio file')
    parser.add_argument('--vcsteps', type=int, required=True, help='Number of diffusion steps')
    parser.add_argument('--output', type=str, required=True, help='Output path for the synthesized audio file')
    args = parser.parse_args()

    sample_rate, audio = clsynthesize(args.text, args.voice, args.vcsteps)

    # Save the synthesized audio to the specified output path
    sf.write(args.output, audio, sample_rate)

if __name__ == "__main__":
    main()