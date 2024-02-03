# Docker Setup

1. Run `installer.sh` (this will set up ComfyUI and create a docker_requirements.txt)
2. Run `docker build -t "storyteller/comfyui" . ` to create the docker container

# Running the container

A folder called `mounts` is where everything will be mounted into the container. Create it and set the
`COMFY_MOUNTS_DIRECTORY` environment variable in the `storyteller-rs` repo.