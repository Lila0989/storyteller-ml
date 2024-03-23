import os
import signal
import subprocess
import time

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil
from pathlib import Path
import asyncio
import uuid
import os
import json
import requests
import random

app = FastAPI()
lock = asyncio.Lock()  # Create an asyncio lock

SERVER_IP = os.environ.get("SERVER_IP", "127.0.0.1:8188")
TIMEOUT_SECONDS = os.environ.get("TIMEOUT_SECONDS", 1000)
PROMPT_ENDPOINT = f"http://{SERVER_IP}/prompt"
PROMPT_FILE = os.environ.get("PROMPT_FILE", "prompt.json")
COMFY_ROOT_DIRECTORY = os.environ.get("COMFY_ROOT_DIRECTORY",
                                      "/home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI")
SERVER_START_TIMEOUT = int(os.environ.get("SERVER_START_TIMEOUT", 60))



def terminate_process(proc):
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def signal_handler(signum, frame):
    print("Signal received, shutting down.")
    terminate_process(comfyui_process)
    exit(0)


@app.post("/preview/")
async def upload_video(video: UploadFile = File(...)):
    async with lock:  # Acquire the lock
        try:
            # Save uploaded video to a temporary directory
            video_filename = f"temp_videos/{uuid.uuid4()}.mp4"  # Use a unique filename
            Path("temp_videos").mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
            with open(video_filename, "wb") as buffer:
                shutil.copyfileobj(video.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")

        # Process video and generate preview
        preview_image_path = await process_video(video_filename)

    return FileResponse(preview_image_path, media_type='image/jpeg')


async def process_video(video_path: str) -> Path:
    json_prompt = json.load(open(PROMPT_FILE))

    # generate random seed (otherwise video will cache completely and not generate a new output)
    json_prompt["173"]["inputs"]["seed"] = random.randint(0, 1000000)

    input_video_path = Path(COMFY_ROOT_DIRECTORY) / "input/input.mp4"
    preview_image_path = Path(COMFY_ROOT_DIRECTORY) / "output/vid2vid/SparseImagePreview_00001_.png"
    shutil.move(video_path, input_video_path)
    if os.path.exists(preview_image_path):
        os.remove(preview_image_path)

    response = requests.get(PROMPT_ENDPOINT, timeout=5)
    if response.status_code == 200:
        print("Server is healthy")
    else:
        print("Server is unhealthy")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        raise HTTPException(status_code=500, detail="Server is unhealthy")

    # make sure there are no jobs already
    queue_json = response.json()
    if queue_json["exec_info"]["queue_remaining"]:
        print("There are jobs in the queue already. Exiting...")
        raise HTTPException(status_code=500, detail="There are jobs in the queue already (this shouldn't happen)")
    else:
        print("Queue is empty")

    p = {"prompt": json_prompt}
    data = json.dumps(p).encode('utf-8')
    response = requests.post(PROMPT_ENDPOINT, data=data)
    if response.status_code == 200:
        print("Job enqueued successfully")
    else:
        print("Job failed to queue")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        raise HTTPException(status_code=500, detail=f"Failed to queue job")

    start_time = time.time()
    while True:
        response = requests.get(PROMPT_ENDPOINT, timeout=5)
        queue_json = response.json()
        if queue_json["exec_info"]["queue_remaining"]:
            pass
        else:
            print("Job is done")
            break
        if time.time() - start_time > TIMEOUT_SECONDS:
            print("Timeout reached and job didn't finish!")
            raise HTTPException(status_code=500, detail="Timeout reached and job didn't finish!")
        time.sleep(1)

    return preview_image_path


if __name__ == "__main__":
    import uvicorn

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    comfyui_process = subprocess.Popen(["venv/bin/python", "main.py"], cwd=COMFY_ROOT_DIRECTORY)

    # block until comfyUI server is up
    start_time = time.time()
    started = False
    while time.time() - start_time < SERVER_START_TIMEOUT:
        try:
            response = requests.get(PROMPT_ENDPOINT, timeout=5)
            if response.status_code == 200:
                print("Server is healthy")
                started = True
                break
        except requests.exceptions.ConnectionError:
            print(f"Server is not up yet. Time elapsed: {time.time() - start_time:.2f}")
        time.sleep(1)
    if not started:
        print(f"Server failed to start in {SERVER_START_TIMEOUT} seconds")
        exit(1)
    print("ComfyUI server running, starting FastAPI server")
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # cleanup
    terminate_process(comfyui_process)
