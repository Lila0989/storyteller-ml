## ComfyRunner

Run a single ComfyUI request from the command line.

### Usage

Put the request parameters into `prompt/prompt.json` and run `ComfyRunner.py`. The ComfyUI folder must be named "ComfyUI" and be in the same superdirectory

### Usage in backend

It must run with the ComfyUI venv, example:
```
COMFY_INFERENCE_ROOT_DIRECTORY="/home/salt/clone/storyteller-ml/image_generation/ComfyUI"
COMFY_INFERENCE_EXECUTABLE_OR_COMMAND="venv/bin/python ../ComfyLauncher/ComfyLauncher.py"
```
