import os
import subprocess
import json
import sys
from pathlib import Path


def get_video_resolution(input_video):
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'json',
        input_video
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    video_info = json.loads(result.stdout)

    width = video_info['streams'][0]['width']
    height = video_info['streams'][0]['height']

    return width, height

def calculate_new_resolution(width, height, max_resolution):
    aspect_ratio = width / height
    max_width, max_height = map(int, max_resolution.split('x'))

    if width > max_width or height > max_height:
        if (max_width / aspect_ratio) <= max_height:
            new_width = max_width
            new_height = round(new_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = round(new_height * aspect_ratio)
    else:
        new_width, new_height = width, height

    new_width = 8 * round(new_width / 8)
    new_height = 8 * round(new_height / 8)

    return new_width, new_height

def format_timestamp(ms):
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{int(ms):03d}"

def process_video(input_video, max_resolution, start_ms, end_ms, framerate):
    width, height = get_video_resolution(input_video)
    print(f"Original resolution: {width}x{height}")

    new_width, new_height = calculate_new_resolution(width, height, max_resolution)
    print(f"New resolution: {new_width}x{new_height}")

    start_time = format_timestamp(start_ms)
    duration_ms = end_ms - start_ms
    duration = format_timestamp(duration_ms)

    # get input video directory
    input_vid_dir = Path(input_video).absolute().parent
    output_video = input_vid_dir.joinpath(f"input.mp4")
    # os.makedirs(os.path.dirname(output_video), exist_ok=True)

    command = [
        'ffmpeg',
        '-y',
        '-i', input_video,
        '-ss', start_time,
        '-t', duration,
        '-vf', f'scale={new_width}:{new_height}',
        '-r', str(framerate),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
        '-c:a', 'aac', '-b:a', '128k',
        output_video
    ]

    subprocess.run(command, check=True)
    print(f"Video processed successfully. Output saved as {output_video}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python script.py <input_video> <max_resolution> <start_ms> <end_ms> <framerate>")
        sys.exit(1)

    input_video = sys.argv[1]
    max_resolution = sys.argv[2]
    start_ms = int(sys.argv[3])
    end_ms = int(sys.argv[4])
    framerate = float(sys.argv[5])

    process_video(input_video, max_resolution, start_ms, end_ms, framerate)
