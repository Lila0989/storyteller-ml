# Use ubuntu as the base image from the hub
# then have to build this as a image.
FROM nvidia/cuda:12.2.0-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y curl

    # Preconfigure package selections (as an example)
RUN echo "package-name package-name/some-option select option-value" | debconf-set-selections && \ 
    apt-get install -y software-properties-common

RUN apt install software-properties-common -y

RUN add-apt-repository ppa:deadsnakes/ppa

RUN sudo apt-get update
RUN sudo apt-get install python3.8 python3.8-venv python3.8-dev

#RUN apt install python3.10 -y
RUN apt-get install -y git
RUN sudo apt install ffmpeg


# Clone the repository

# RUN pwd
RUN pip3 install requirements-pinned.txt

# Navigate to the cloned directory and checkout the specific commit
WORKDIR TestingDockerIO
COPY VALL-E-X . 

RUN git pull
RUN git reset --hard origin/main
#RUN git checkout 47c491a29d10c04c6f1efd01bc7b334d11cad4f2

# # Allow parameters to be passed
ENTRYPOINT ["python3", "main.py"]
