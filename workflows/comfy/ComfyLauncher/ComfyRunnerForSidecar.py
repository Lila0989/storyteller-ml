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

SERVER_IP = os.environ.get("SERVER_IP", "127.0.0.1:8188")
TIMEOUT_SECONDS = int(os.environ.get("TIMEOUT_SECONDS", 1000))
PROMPT_ENDPOINT = f"http://{SERVER_IP}/prompt"
V2V_WORKFLOWS_DIRECTORY = os.environ.get("V2V_WORKFLOWS_DIRECTORY",
                                         "/workflow_configs")
COMFY_ROOT_DIRECTORY = os.environ.get("COMFY_ROOT_DIRECTORY",
                                      "/app/ComfyUI")

MAIN_IPA_WORKFLOW = os.environ.get("MAIN_IPA_WORKFLOW", "ipa_API_03-05-2024/yae_vid2vid_main(+IPA)_03-05_API.json")
FACE_DETAILER_WORKFLOW = os.environ.get("FACE_DETAILER_WORKFLOW", "yae_vid2vid_FaceDetailer_03-05_API.json")
UPSCALER_WORKFLOW = os.environ.get("UPSCALER_WORKFLOW", "yae_vid2vid_Upscale_03-05_API.json")


class PipelineType(IntEnum):
    BASE = auto()
    IPA = auto()
    FACE_DETAILER = auto()
    UPSCALER = auto()



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
    "hr_giger": "17_hr_giger.json",
    "simpsons": "18_simpsons.json",
    "carnage": "19_carnage.json",
    "pastel_cute_anime": "20_pastel_cute_anime.json",
    "bloom_lighting": "21_bloom_lighting.json",
    "25d_horror": "22_25D_Horror.json",
    "creepy": "23_creepy.json",
    "creepy_vhs": "24_creepy_vhs.json",
    "trail_cam_footage": "25_trail_cam_footage.json",
    "old_black_white_movie": "26_old_black_white_movie.json",
    "horror_noir_black_white": "27_horror_noir_black_white.json",
    "techno_noir_black_white": "28_techno_noir_black_white.json",
    "black_white_20s": "29_black_white_20s.json",
    "cyberpunk_anime": "30_cyberpunk_anime.json",
    "dragonball": "31_dragonball.json",
    "realistic_matrix": "32_realistic_matrix.json",
    "realistic_cyberpunk": "33_realistic_cyberpunk.json"
}


def ensure_pipeline_input_present():
    left = Path(COMFY_ROOT_DIRECTORY) / "input/input.mp4"
    right = Path(COMFY_ROOT_DIRECTORY) / "ComfyUI" / "input/input.mp4"
    shutil.copy(left, right)


def convert_pipline_output_to_input(left):
    right = Path(COMFY_ROOT_DIRECTORY) / "input/input.mp4"
    shutil.copy(left, right)


def restore_last_pipeline_output(left):
    right = Path(COMFY_ROOT_DIRECTORY) / "output" / "vid2vid/SparseUpscaleInterp_00001.mp4"
    shutil.copy(left, right)


def parse_args():
    parser = argparse.ArgumentParser(description='Run Comfy')
    parser.add_argument('--prompt', type=str, help='location of the prompt json', required=False)
    parser.add_argument('--style', type=str, help='style name', required=False)
    parser.add_argument('--positive_prompt_filename', type=str, help='positive prompt', required=False)
    parser.add_argument('--negative_prompt_filename', type=str, help='negative prompt', required=False)
    parser.add_argument('--pause-between-steps', type=int, help='pause between steps', required=False, default=1)
    parser.add_argument('--face-detailer-enabled', help='face detailer enabled', required=False, default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument('--upscaler-enabled', help='upscale enabled', required=False, default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument('--lipsync-enabled', help='lipsync enabled', required=False, default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument('--strength', type=float, help='strength', required=False, default=1.0)
    return parser.parse_args()

args = parse_args()

def ensure_server_is_healthy():
    # check the health of the server (5 second timeout)
    response = requests.get(PROMPT_ENDPOINT, timeout=5)
    if response.status_code == 200:
        print("Server is healthy")
    else:
        print("Server is unhealthy")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

    # make sure there are no jobs already
    queue_json = response.json()
    if queue_json["exec_info"]["queue_remaining"]:
        print("There are jobs in the queue already. Exiting...")
        exit(1)
    else:
        print("Queue is empty")

def main():
    ensure_server_is_healthy()

    pipeline_type = PipelineType.BASE
    if args.face_detailer_enabled or args.upscaler_enabled:
        pipeline_type = PipelineType.IPA

    output_index = 0
    file_path = args.prompt
    prompt = None
    if args.style is not None:
        print("Generating prompt json")
        style = args.style
        positive_prompt_filename = args.positive_prompt_filename
        negative_prompt_filename = args.negative_prompt_filename
        positive_prompt = None
        negative_prompt = None
        workflow_filename = None
        enable_lipsync = args.lipsync_enabled
        if pipeline_type == PipelineType.IPA:
            workflow_filename = MAIN_IPA_WORKFLOW
        if positive_prompt_filename:
            positive_prompt = open(positive_prompt_filename).read()
        if negative_prompt_filename:
            negative_prompt = open(negative_prompt_filename).read()
        validate_style_name(style)
        print("running pipeline" + str(pipeline_type))
        # ensure_pipeline_input_present()
        prompt = generate_prompt_for_style(style, positive_prompt, negative_prompt, workflow_filename, 
                                           enable_lipsync=enable_lipsync)
        enqueue_prompt_and_wait(prompt)
        output_index = output_index + 1
        left = Path(COMFY_ROOT_DIRECTORY) / "output" / f"vid2vid/SparseUpscaleInterp_0000{output_index}.mp4"
        if args.upscaler_enabled:
            # time.sleep(30)
            print("running pipeline" + str(pipeline_type))
            convert_pipline_output_to_input(left)
            workflow_filename = UPSCALER_WORKFLOW
            prompt = generate_prompt_for_style(style, positive_prompt, negative_prompt, workflow_filename, PipelineType.UPSCALER, 
                                               enable_lipsync=enable_lipsync)
            enqueue_prompt_and_wait(prompt)
            output_index = output_index + 1
            left = Path(COMFY_ROOT_DIRECTORY) / "output" / f"vid2vid/SparseUpscaleInterp_0000{output_index}.mp4"
            # time.sleep(30)
        if args.face_detailer_enabled:
            # time.sleep(30)
            print("running pipeline" + str(pipeline_type))
            convert_pipline_output_to_input(left)
            workflow_filename = FACE_DETAILER_WORKFLOW
            prompt = generate_prompt_for_style(style, positive_prompt, negative_prompt, workflow_filename, PipelineType.FACE_DETAILER, 
                                               enable_lipsync=enable_lipsync)
            enqueue_prompt_and_wait(prompt)
            output_index = output_index + 1
            left = Path(COMFY_ROOT_DIRECTORY) / "output" / f"vid2vid/SparseUpscaleInterp_0000{output_index}.mp4"
            # time.sleep(30)
            restore_last_pipeline_output(left)
    else:
        print(f'Loading prompt json from path: {file_path}')
        prompt_workflow = json.load(open(file_path))
        prompt = {"prompt": prompt_workflow}
        enqueue_prompt_and_wait(prompt)

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
        response = requests.get(PROMPT_ENDPOINT, timeout=5)
        queue_json = response.json()
        if queue_json["exec_info"]["queue_remaining"]:
            pass
        else:
            print("Job is done")
            break
        if time.time() - start_time > TIMEOUT_SECONDS:
            print("Timeout reached and job didn't finish!")
            exit(1)
        time.sleep(1)



def generate_prompt_for_style(style_name, positive_prompt, negative_prompt, workflow_filename=None, pipeline_type = PipelineType.BASE,
                              enable_lipsync: bool = False) -> Path:
    styles_directory = Path(V2V_WORKFLOWS_DIRECTORY) / "styles"
    workflow_directory = Path(V2V_WORKFLOWS_DIRECTORY) / "workflows"
    mappings_directory = Path(V2V_WORKFLOWS_DIRECTORY) / "mappings"

    style_filename = style_to_filename[style_name]
    style_json = json.load(open(styles_directory / style_filename))

    workflow_json_filename = style_json["workflow_api_name"]
    mapping_json_filename = "mapping_one.json"

    if workflow_filename:
        workflow_json_filename = workflow_filename

    workflow_json = json.load(open(workflow_directory / workflow_json_filename))
    mapping_json = json.load(open(mappings_directory / mapping_json_filename))

    json_mods = style_json["modifications"]
    jsonpath_mods = get_jsonpath_mods(json_mods, mapping_json, pos_in=positive_prompt, neg_in=negative_prompt, pipeline_type=pipeline_type, 
                                      enable_lipsync=enable_lipsync)

    print(*jsonpath_mods.items(), sep="\n")

    json_prompt = apply_jsonpath_mods(jsonpath_mods, workflow_json)

    p = {"prompt": json_prompt}
    return p


def get_jsonpath_mods(style_mods: Dict[str, Any], mapping_json: Dict[str, Any], pos_in: Optional[str] = None,
                      neg_in: Optional[str] = None, pipeline_type = PipelineType.BASE, denoise_first_pass=1.0,
                      enable_lipsync: bool = False) -> Dict[str, Any]:
    modifications = {}
    new_mod_json = style_mods.copy()
    # Process "loras" differently
    loras = new_mod_json.get("loras", [])
    if len(loras) > 8:
        raise ValueError("Too many loras, max is 8")

    for index, lora in enumerate(loras):
        if "name" in lora and "strength" in lora:
            lora_strength = lora["strength"]
            if pipeline_type == PipelineType.FACE_DETAILER:
                lora_strength = 0.5
            new_mod_json[f"lora_{index + 1}_strength"] = lora_strength
            new_mod_json[f"lora_{index + 1}_name"] = lora["name"]

    # Exclude "loras" from further processing
    new_mod_json.pop("loras", None)

    # Handling positive and negative prompts
    if pos_in:
        new_mod_json["positive_prompt"] = f"{new_mod_json.get('positive_prompt', '')}, {pos_in}"
    if neg_in:
        new_mod_json["negative_prompt"] = f"{new_mod_json.get('negative_prompt', '')}, {neg_in}"

    if pipeline_type == PipelineType.IPA:
        new_mod_json["denoise_first_pass"] = denoise_first_pass

    if enable_lipsync:
        new_mod_json["cn_lips_strength"] = 1.2

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


def validate_style_name(style):
    if style not in style_to_filename:
        print(f"Invalid style: {args.style}")
        print(f"Valid styles: {', '.join(style_to_filename.keys())}")
        exit(1)

if __name__ == "__main__":
    main()