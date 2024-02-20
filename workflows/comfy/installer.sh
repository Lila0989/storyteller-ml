#!/bin/bash

# Check if exactly one argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <create-docker-requirements: yes/no>"
    exit 1
fi

rm -rf ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
python3 -m venv ComfyUI/venv
ComfyUI/venv/bin/pip install -r ComfyUI/requirements.txt
echo "ComfyUI has been installed successfully!"

ComfyUI/venv/bin/python3 initialize_comfy_extensions.py
echo "Extensions have been installed successfully!"

# Check if the argument is 'yes' to create Docker requirements
if [ "$1" == "yes" ]; then
    ComfyUI/venv/bin/pip freeze > docker_requirements.txt
    echo "Requirements have been saved to docker_requirements.txt"
    echo "Removing venv..."
    rm -rf ComfyUI/venv
fi

exit 0
