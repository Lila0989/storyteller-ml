docker run --rm \
--gpus all \
--publish 8188:8188 \
--user $(id -u):$(id -g) \
-v $(pwd)/mounts/models/checkpoints:/app/ComfyUI/models/checkpoints \
-v $(pwd)/mounts/models/loras:/app/ComfyUI/models/loras \
-v $(pwd)/mounts/models/controlnet:/app/ComfyUI/models/controlnet \
-v $(pwd)/mounts/models/ipadapter:/app/ComfyUI/models/ipadapter \
-v $(pwd)/mounts/models/clip_vision:/app/ComfyUI/models/clip_vision \
-v $(pwd)/mounts/prompt:/app/ComfyLauncher/prompt \
-v $(pwd)/mounts/output:/app/ComfyUI/output \
-v $(pwd)/mounts/input:/app/ComfyUI/input \
-v $(pwd)/mounts/custom_nodes/ComfyUI-AnimateDiff-Evolved/models:/app/ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved/models \
-v $(pwd)/mounts/custom_nodes/comfyui_controlnet_aux/ckpts:/app/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts \
-v $(pwd)/mounts/custom_nodes/ComfyUI-Frame-Interpolation/ckpts:/app/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts \
-it "storyteller/comfyui" python3 /app/ComfyLauncher/ComfyRunner.py

# -it "test" /bin/bash