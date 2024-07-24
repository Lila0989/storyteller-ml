import requests
import argparse
import os
import json
import time
from typing import Dict, Any, Optional
from jsonpath_ng import jsonpath, parse
import shutil
from pathlib import Path
from enum import IntEnum, auto
import os
import subprocess
import signal

SERVER_IP = os.environ.get("SERVER_IP", "127.0.0.1:8188")
SERVER_START_TIMEOUT = int(os.environ.get("SERVER_START_TIMEOUT", 180))

TIMEOUT_SECONDS = int(os.environ.get("TIMEOUT_SECONDS", 1000))
PROMPT_ENDPOINT = f"http://{SERVER_IP}/prompt"
V2V_WORKFLOWS_DIRECTORY = os.environ.get("V2V_WORKFLOWS_DIRECTORY",
                                         "/workflow_configs")


COMFY_ROOT_DIRECTORY = os.environ.get("COMFY_ROOT_DIRECTORY",
                                      "/app/ComfyUI")


BASE_LIVE_PORTRAIT_WORKFLOW = os.environ.get("BASE_LIVE_PORTRAIT_WORKFLOW", "17-07-2024/yae_LivingPortrait_17-07_API.json")

# V2V_WORKFLOWS_DIRECTORY = "/app/ComfyUI/exp"
# BASE_LIVE_PORTRAIT_WORKFLOW = "yae_LivingPortrait_17-07_API.json"

class PipelineType(IntEnum):
    BASE = auto()


def ensure_input_directory_empty():
    input_directory = Path(COMFY_ROOT_DIRECTORY) / "input"
    for file in input_directory.iterdir():
        if file.is_file():
            file.unlink()

def ensure_output_directory_empty():
    output_directory = Path(COMFY_ROOT_DIRECTORY) / "output" / "vid2vid"
    for file in output_directory.iterdir():
        if file.is_file():
            print('deleteing file: ' + str(file) )
            file.unlink()

def ensure_pipeline_input_present(source_path, input_name=None):
    left = Path(source_path)
    left_filename = left.name
    right_filename = left_filename
    if input_name is not None:
        right_filename = input_name
    right = Path(COMFY_ROOT_DIRECTORY) / "input" / right_filename
    shutil.copy(left, right)


def ensure_output_present_at(new_filename):
    directory = Path(COMFY_ROOT_DIRECTORY) / "output" / "vid2vid"
    # Comfy will create a copy of the video that includes audio, but only if the driver video had audio.
    output = directory / "LivePortrait_00001.mp4"
    output_with_audio = directory / "LivePortrait_00001-audio.mp4"
    if os.path.exists(output_with_audio):
        output = output_with_audio
    shutil.copy(output, new_filename)

def parse_args():
    parser = argparse.ArgumentParser(description='Run Comfy')
    parser.add_argument('--portrait-media-filename', type=str, help='path of mp4 depth from engine for preprocessing', required=True)
    parser.add_argument('--driver-media-filename', type=str, help='path of mp4 outline from engine for preprocessing', required=True)
    parser.add_argument('--input-is-image', action='store_true', help='input is image', required=True)
    parser.add_argument('--skip-comfy-startup', action='store_true', help='controls if this script tries to start comfy', default=True)
    parser.add_argument('--tmpdir', type=str, help='path of tmpdir for preprocessing', required=False)
    parser.add_argument('--output-filename', type=str, help='path of output filename', required=True)


    return parser.parse_args()

args = parse_args()

def ensure_server_is_healthy(server_address):
    # check the health of the server (5 second timeout)
    response = requests.get(f"http://{server_address}/queue", timeout=5)
    if response.status_code == 200:
        print("Server is healthy")
    else:
        print("Server is unhealthy")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

    # make sure there are no jobs already
    queue_json = response.json()
    if len(queue_json.get("queue_pending", [])) > 0:
        print("There are jobs in the queue already. Exiting...")
        exit(1)
    else:
        print("Queue is empty")



def main():
    ensure_server_is_healthy(SERVER_IP)
    pipeline_type = PipelineType.BASE
    workflow_filename = BASE_LIVE_PORTRAIT_WORKFLOW
    input_media_filename = args.portrait_media_filename
    input_driver_filename = args.driver_media_filename
    input_is_image = args.input_is_image
    ensure_input_directory_empty()
    ensure_output_directory_empty()
    input_filename = "input.mp4"
    if input_media_filename:
        if input_is_image:
            ensure_pipeline_input_present(input_media_filename)
            input_filename = Path(input_media_filename).name
        else:
            ensure_pipeline_input_present(input_media_filename, "input.mp4")

    if input_driver_filename:
        ensure_pipeline_input_present(input_driver_filename, "driver.mp4")


    time_before = time.perf_counter()
    print("Generating prompt json using workflow: " + workflow_filename)

    prompt = generate_prompt_for_style(
        workflow_filename=workflow_filename,
        input_media_filename="input/" + input_filename,
        input_driver_filename="input/driver.mp4",
        input_is_image=input_is_image,
    )
    print("running pipeline" + str(pipeline_type))
    enqueue_prompt_and_wait(prompt)

    ensure_output_present_at(args.output_filename)
    time_after = time.perf_counter()
    print(f"Time taken: {time_after - time_before:.2f} seconds")


def enqueue_prompt_and_wait(prompt):
    data = json.dumps(prompt).encode('utf-8')
    # Send HTTP post request
    response = requests.post(PROMPT_ENDPOINT, data=data)
    if response.status_code == 200:
        print("Job enqueued successfully")
    else:
        print("Job failed to queue")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)

    # Wait for the job to finish
    print(f"Waiting for job to finish (timeout: {TIMEOUT_SECONDS} seconds)")
    start_time = time.time()
    # check queue endpoint in loop
    while True:
        try:
            response = requests.get(PROMPT_ENDPOINT, timeout=5)
            queue_json = response.json()
            if queue_json["exec_info"]["queue_remaining"]:
                pass
            else:
                print("Job is done")
                break
        except Exception:
            print("Error while checking queue")
            time.sleep(1)
            continue
        if time.time() - start_time > TIMEOUT_SECONDS:
            print("Timeout reached and job didn't finish!")
            exit(1)
        time.sleep(1)



def generate_prompt_for_style(
                              workflow_filename: str,
                              input_media_filename: Optional[str] = None,
                                input_driver_filename: Optional[str] = None,
                                input_is_image: Optional[bool] = False,
                            ):
    workflow_directory = Path(V2V_WORKFLOWS_DIRECTORY) / "workflows"


    if workflow_filename:
        workflow_json_filename = workflow_filename

    workflow_json = json.load(open(workflow_directory / workflow_json_filename))


    jsonpath_mods = {
        "$.25.inputs.video": input_driver_filename
    }

    if input_is_image:
        jsonpath_mods["$.43.inputs.image_path"] = input_media_filename
        jsonpath_mods["$.26.inputs.video"] = input_driver_filename
        jsonpath_mods["$.46.inputs.boolean"] = 0
    else:
        jsonpath_mods["$.26.inputs.video"] = input_media_filename
        jsonpath_mods["$.46.inputs.boolean"] = 1

    print(*jsonpath_mods.items(), sep="\n")

    json_prompt = apply_jsonpath_mods(jsonpath_mods, workflow_json)

    p = {"prompt": json_prompt}
    return p

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
    os.setpgrp()
    try:
        if not args.skip_comfy_startup:
            comfyui_process = subprocess.Popen(["../venv/bin/python", "main.py", "--highvram", "--disable-metadata"], cwd=COMFY_ROOT_DIRECTORY)
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
        main()
    finally:
        os.killpg(0, signal.SIGKILL) # kill all processes in my group
