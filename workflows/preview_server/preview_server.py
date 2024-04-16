import signal
import subprocess
import time

import shutil
from pathlib import Path
import asyncio
import uuid
import os
import json
import random
from typing import Dict, Any, Optional
import mimetypes

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import FileResponse
import requests
from jsonpath_ng import jsonpath, parse
from moviepy.editor import ImageClip

app = FastAPI()
lock = asyncio.Lock()  # Create an asyncio lock

SERVER_IP = os.environ.get("SERVER_IP", "127.0.0.1:8188")
TIMEOUT_SECONDS = os.environ.get("TIMEOUT_SECONDS", 1000)
PROMPT_ENDPOINT = f"http://{SERVER_IP}/prompt"
V2V_WORKFLOWS_DIRECTORY = os.environ.get("V2V_WORKFLOWS_DIRECTORY",
                                         "/home/salt/clone/storyteller/V2V-StylesList/V2VWorkflows/")
COMFY_ROOT_DIRECTORY = os.environ.get("COMFY_ROOT_DIRECTORY",
                                      "/home/salt/clone/storyteller/storyteller-ml/workflows/preview_server/ComfyUI")
SERVER_START_TIMEOUT = int(os.environ.get("SERVER_START_TIMEOUT", 60))
STYLE_LOCK = os.environ.get("STYLE_LOCK", None)
PREVIEW_WORKFLOW_NAME = os.environ.get("PREVIEW_WORKFLOW_NAME", None)
MAPPING_NAME = os.environ.get("MAPPING_NAME", "mapping_two.json")
AUTH_URL = os.environ.get("AUTH_URL", "https://api.fakeyou.com/v1/session")

style_to_filename = {
    "anime_2_5d": "1_2.5d_anime_model.json",
    "anime_2d_flat": "2_2d_flat_anime_model.json",
    "cartoon_3d": "3_3d_cartoon_style.json",
    "comic_book": "4_comic_book_model.json",
    "anime_ghibli": "5_ghibli_anime_model.json",
    "ink_punk": "6_ink_punk.json",
    "ink_splash": "7_ink_splash.json",
    "ink_bw_style": "8_ink_w_and_b_style.json",
    "jojo_style": "9_jojo_style.json",
    "paper_origami": "10_paper_origami.json",
    "pixel_art": "11_pixel_art.json",
    "pop_art": "12_pop_art.json",
    "realistic_1": "13_realistic_1.json",
    "realistic_2": "14_realistic_2.json",
    "anime_retro_neon": "15_retro_neon_anime_90.json",
    "anime_standard": "16_standard_anime_model.json",
}

allowed_keys = ["style", "positive_prompt", "negative_prompt"]

# CORS header for which websites can import this content in a frame.
# This *technically* shouldn't be required, but the XHR requests are 
# being made from a controlled frame.
#
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors
#
# NB(bt,2024-03-30): The *.netlify.app is dangerous.
CORS_FRAME_ANCESTORS = [
    "frame-ancestors 'self'",
    "https://studio.storyteller.ai",
    "https://storytellerstudio.netlify.app",
    "https://fakeyou.com",
    "https://*.fakeyou.com",
    "https://storyteller.ai",
    "https://*.storyteller.ai",
    "https://*.netlify.app",
    "http://*.fakeyou.com:7000",
    "http://*.fakeyou.com:7001",
    "http://*.fakeyou.com:7002",
    "http://*.storyteller.ai:7000",
    "http://*.storyteller.ai:7001",
    "http://*.storyteller.ai:7002",
    ";",
]


def can_use_vst(cookies):
    """Check if the user is authenticated and if the 'video_style_transfer' feature flag is enabled."""
    try:
        response = requests.get(AUTH_URL, cookies=cookies)
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return False

    if response.status_code == 200:
        try:
            response_json = response.json()
        except ValueError:
            print("Invalid JSON response")
            return False

        if response_json.get("success") and response_json.get("logged_in"):
            username = response_json["user"]["core_info"]["username"]
            print(f"User is logged in: {username}")
            feature_flags = response_json["user"].get("maybe_feature_flags", {})
            if "video_style_transfer" in feature_flags:
                print("VST feature flag is found")
                return True
            else:
                print("VST feature flag not found")
        else:
            print("User is not logged in or session is invalid")
    else:
        print(f"Failed to authenticate ({response.status_code}): {response.text}")

    return False


def validate_request(request):
    try:
        request = json.loads(request)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for 'request'")
    # check for style key
    if "style" not in request:
        raise HTTPException(status_code=400, detail="Missing 'style' key in 'request'")
    style = request["style"]
    if style not in style_to_filename:
        raise HTTPException(status_code=400,
                            detail=f"Invalid 'style' key in 'request'. Valid styles: {', '.join(style_to_filename.keys())}")
    # check for other keys
    for key in request:
        if key not in allowed_keys:
            raise HTTPException(status_code=400,
                                detail=f"Invalid key '{key}' in 'request'. Valid keys: {', '.join(allowed_keys)}")
    return request


def terminate_process(proc):
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def signal_handler(signum, frame):
    print("Signal received, shutting down.")
    terminate_process(comfyui_process)
    print("ComfyUI server terminated")
    exit(0)


@app.post("/preview/")
async def preview_request(request_obj: Request, request: str = Form(...), input_file: UploadFile = File(...)):
    cookies = request_obj.cookies
    if not can_use_vst(cookies):
        raise HTTPException(status_code=401, detail="No Video Style Transfer feature flag found")

    request = validate_request(request)

    if STYLE_LOCK:
        if request["style"] != STYLE_LOCK:
            raise HTTPException(status_code=400, detail=f"This endpoint is for '{STYLE_LOCK}' style only")

    async with lock:
        try:
            style_filename = style_to_filename[request["style"]]
            positive_prompt = request.get("positive_prompt", None)
            negative_prompt = request.get("negative_prompt", None)

            temp_filename = f"temp_files/{uuid.uuid4()}"
            Path(temp_filename).parent.mkdir(parents=True, exist_ok=True)
            with open(temp_filename, "wb") as buffer:
                shutil.copyfileobj(input_file.file, buffer)

            mime_type, _ = mimetypes.guess_type(input_file.filename)

            if 'video' in mime_type:
                input_filename = f"{temp_filename}.mp4"
            elif 'image' in mime_type:
                input_filename = f"{temp_filename}.{mime_type.split('/')[-1]}"
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")

            Path(temp_filename).rename(input_filename)

            if 'image' in mime_type:
                clip = ImageClip(input_filename)
                fps = 24
                clip_duration = 1 / fps
                clip = clip.set_duration(clip_duration)
                input_filename = f"temp_files/{uuid.uuid4()}.mp4"
                clip.write_videofile(input_filename, fps=fps)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

        # Process video (or image converted to video) and generate preview
        preview_image_path = await process_video(input_filename, style_filename, positive_prompt, negative_prompt)

    csp_frame_ancestors_value = ' '.join(CORS_FRAME_ANCESTORS[:-1])
    headers = {
        "Access-Control-Allow-Origin": "*",  # Be cautious with this setting in production environments.
        "Content-Security-Policy": f"frame-ancestors {csp_frame_ancestors_value}",
    }

    return FileResponse(preview_image_path, media_type='image/jpeg', headers=headers)


async def process_video(video_path: str, style_filename, positive_prompt=None, negative_prompt=None) -> Path:
    # generate random seed (otherwise video will cache completely and not generate a new output)
    styles_directory = Path(V2V_WORKFLOWS_DIRECTORY) / "styles"
    workflow_directory = Path(V2V_WORKFLOWS_DIRECTORY) / "workflows"
    mappings_directory = Path(V2V_WORKFLOWS_DIRECTORY) / "mappings"

    style_json = json.load(open(styles_directory / style_filename))
    workflow_json = json.load(open(workflow_directory / PREVIEW_WORKFLOW_NAME))
    # mapping_json = json.load(open(mappings_directory / style_json["mapping_name"]))
    mapping_json = json.load(open(mappings_directory / MAPPING_NAME))

    json_mods = style_json["modifications"]
    jsonpath_mods = get_jsonpath_mods(json_mods, mapping_json, pos_in=positive_prompt, neg_in=negative_prompt)
    print(*jsonpath_mods.items(), sep="\n")

    json_prompt = apply_jsonpath_mods(jsonpath_mods, workflow_json)

    # generate random seed (otherwise video will cache completely and not generate a new output)
    try:
        json_prompt["173"]["inputs"]["seed"] = random.randint(0, 1000000)
    except KeyError:
        pass

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


def get_jsonpath_mods(style_mods: Dict[str, Any], mapping_json: Dict[str, Any], pos_in: Optional[str] = None,
                      neg_in: Optional[str] = None) -> Dict[str, Any]:
    modifications = {}
    new_mod_json = style_mods.copy()
    # Process "loras" differently
    loras = new_mod_json.get("loras", [])
    if len(loras) > 8:
        raise ValueError("Too many loras, max is 8")

    for index, lora in enumerate(loras):
        if "name" in lora and "strength" in lora:
            new_mod_json[f"lora_{index + 1}_strength"] = lora["strength"]
            new_mod_json[f"lora_{index + 1}_name"] = lora["name"]

    # Exclude "loras" from further processing
    new_mod_json.pop("loras", None)

    # Handling positive and negative prompts
    if pos_in:
        new_mod_json["positive_prompt"] = f"{new_mod_json.get('positive_prompt', '')}, {pos_in}"
    if neg_in:
        new_mod_json["negative_prompt"] = f"{new_mod_json.get('negative_prompt', '')}, {neg_in}"

    for key, value in new_mod_json.items():
        mapping_key = f"$.{key}"
        jsonpath_expr = parse(mapping_key)

        # Finding matches using jsonpath_ng
        matches = [match.value for match in jsonpath_expr.find(mapping_json)]
        if matches:
            mapping_value = matches[0]
            modifications[mapping_value] = value
        else:
            print(f"No mapping found for key '{key}'")

    return modifications


def apply_jsonpath_mods(jsonpath_mods: Dict[str, Any], workflow_json: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in jsonpath_mods.items():
        # jsonpath-ng expects numbers to be wrapped in quotes
        parts = key.split(".")
        new_parts = [f"'{part}'" if part.isdigit() else part for part in parts]
        key = ".".join(new_parts)

        jsonpath_expr = parse(key)
        matches = jsonpath_expr.find(workflow_json)

        if matches:
            parent = matches[0].context.value

            if isinstance(parent, dict):
                last_part = new_parts[-1].strip("'")
                parent[last_part] = value

            elif isinstance(parent, list):
                index = int(new_parts[-1].strip("'"))
                if 0 <= index < len(parent):
                    parent[index] = value
                else:
                    print(f"Index {index} is out of bounds for key '{key}'")
        else:
            print(f"No mapping found for key '{key}'")

    return workflow_json


if __name__ == "__main__":
    import uvicorn
    import asyncio

    # install ComfyUI
    os.system("python3 install.py")

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # cleanup
    terminate_process(comfyui_process)
