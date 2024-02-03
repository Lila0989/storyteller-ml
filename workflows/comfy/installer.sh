python3 -m venv ComfyUI/venv
ComfyUI/venv/bin/pip install -r ComfyUI/requirements.txt
echo "ComfyUI has been installed successfully!"
ComfyUI/venv/bin/python3 initialize_comfy_extensions.py
echo "Extensions have been installed successfully!"
ComfyUI/venv/bin/pip freeze > docker_requirements.txt
echo "Requirements have been saved to docker_requirements.txt"
echo "Removing venv..."
rm -rf ComfyUI/venv
exit 0
