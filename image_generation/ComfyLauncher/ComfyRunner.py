import asyncio
import os
import sys


comfy_path = os.path.dirname(os.path.abspath(__file__))
comfy_path = os.path.join(comfy_path, '..', 'ComfyUI')

# change to ComfyUI directory
os.chdir(comfy_path)

# add ComfyUI to path
sys.path.append(comfy_path)

from server import PromptServer
from execution import PromptQueue

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
server = PromptServer(loop)
q = PromptQueue(server)