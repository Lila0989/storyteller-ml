import subprocess
import json
import os

# set cwd to script location
os.chdir(os.path.dirname(os.path.realpath(__file__)))

json_file_path = 'repos.json'
venv_python = os.path.join('ComfyUI', 'venv', 'Scripts' if os.name == 'nt' else 'bin', 'python')


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Print stdout live
    for line in iter(process.stdout.readline, ''):
        print(line, end='')

    # Wait for the process to terminate and get the exit code
    process.wait()

    # Check if the process exited with an error
    if process.returncode != 0:
        # Print any errors from stderr
        for line in iter(process.stderr.readline, ''):
            print(line, end='')
        print(f"Error executing command: {command}")


def setup_repo(repo_info):
    url, commit, folder = repo_info['url'], repo_info['commit'], repo_info['folder']
    # save the current working directory
    original_cwd = os.getcwd()
    try:
        run_command(f"git clone {url} {folder}")
        os.chdir(folder)
        run_command(f"git checkout {commit}")
    finally:
        os.chdir(original_cwd)


def setup_venv_and_install_requirements():
    run_command("python3 -m venv ComfyUI/venv")
    print('=============# Installing ComfyUI Requirements #=============')
    run_command(f"{venv_python} -m pip install -r ComfyUI/requirements.txt")
    print('=============# Installing extension missing requirements #=============')
    run_command(f"{venv_python} -m pip install -r required_requirements.txt")


def run_comfyui_setup():
    run_command(f"{venv_python} initialize_comfy_extensions.py")


def main():
    with open(json_file_path, 'r') as file:
        repos = json.load(file)

    for repo_info in repos:
        print(f"installing {repo_info['url']} at commit {repo_info['commit']} to {repo_info['folder']}")
        setup_repo(repo_info)

    setup_venv_and_install_requirements()
    run_comfyui_setup()


if __name__ == "__main__":
    main()
    open('ALREADY_SETUP.flag', 'w').close()
