docker run --rm \
--gpus all \
--publish 8188:8188 \
--user $(id -u):$(id -g) \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/models/checkpoints:/app/ComfyUI/models/checkpoints \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/models/loras:/app/ComfyUI/models/loras \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/models/controlnet:/app/ComfyUI/models/controlnet \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/models/ipadapter:/app/ComfyUI/models/ipadapter \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/models/clip_vision:/app/ComfyUI/models/clip_vision \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/prompt:/app/ComfyLauncher/prompt \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/output:/app/ComfyUI/output \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/input:/app/ComfyUI/input \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved/models:/app/ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved/models \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts:/app/ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts \
-v /home/salt/clone/storyteller/storyteller-ml/workflows/comfy/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts:/app/ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts \
-it "comfyui/testing" python3 /app/ComfyLauncher/ComfyRunner.py --prompt /app/ComfyLauncher/prompt/prompt.json

# -it "test" /bin/bash
