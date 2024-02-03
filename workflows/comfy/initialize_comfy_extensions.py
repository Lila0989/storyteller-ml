import asyncio
import json
import os
import subprocess
import sys
import threading


def clone_repos(file_name, destination_folder_name):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the full path for the file
    file_path = os.path.join(script_dir, file_name)

    # Construct the full path for the destination folder and change into it
    destination_folder = os.path.join(script_dir, destination_folder_name)
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    os.chdir(destination_folder)

    with open(file_path, 'r') as file:
        for repo_url in file:
            repo_url = repo_url.strip()
            if repo_url:
                try:
                    # Execute the git clone command
                    cmd = ['git', 'clone', repo_url]
                    subprocess.run(cmd, check=True)
                    print(f"Successfully cloned {repo_url}")
                except subprocess.CalledProcessError:
                    print(f"Failed to clone {repo_url}")


# Name of the file containing the Git repos, relative to the script
file_name = 'required_extensions.txt'  # The file should be in the same directory as the script

# Name of the destination folder, relative to the script
# destination_folder_name = 'ComfyUI/custom_nodes'
destination_folder_name = 'ComfyUI/custom_nodes'

# Clone the repositories
clone_repos(file_name, destination_folder_name)

# install extra requirements

# get executable
executable = sys.executable

script_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(script_dir, 'required_requirements.txt')

# install
cmd = [executable, '-m', 'pip', 'install', '-r', file_path]
subprocess.run(cmd, check=True)

# Init all the nodes

current_script_dir = os.path.dirname(os.path.realpath(__file__))
comfy_path = os.path.dirname(os.path.abspath(__file__))
comfy_path = os.path.join(comfy_path, 'ComfyUI')

# change to ComfyUI directory
os.chdir(comfy_path)

# add ComfyUI to path
sys.path.append(comfy_path)

from server import PromptServer
from execution import PromptQueue
from main import init_custom_nodes, cuda_malloc_warning, prompt_worker, execute_prestartup_script
import folder_paths

execute_prestartup_script()

async def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = PromptServer(loop)
    q = PromptQueue(server)

    init_custom_nodes()

    cuda_malloc_warning()

    server.add_routes()

    threading.Thread(target=prompt_worker, daemon=True, args=(q, server,)).start()

    folder_paths.add_model_folder_path("checkpoints", os.path.join(folder_paths.get_output_directory(), "checkpoints"))
    folder_paths.add_model_folder_path("clip", os.path.join(folder_paths.get_output_directory(), "clip"))
    folder_paths.add_model_folder_path("vae", os.path.join(folder_paths.get_output_directory(), "vae"))

    await server.start('127.0.0.1', 8188)


if __name__ == "__main__":
    asyncio.run(run())
