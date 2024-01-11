# Use NVIDIA CUDA with Ubuntu as the base image
FROM nvidia/cuda:12.2.0-devel-ubuntu20.04

# Set environment variables
ENV MY_ENV_VARIABLE=value
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    software-properties-common \
    git \
    ffmpeg \
    espeak-ng \
    sudo \
    python3.10 \
    python3-pip

# Install git-lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
    && apt-get install git-lfs \
    && git lfs install

# Create a directory for your project
WORKDIR /TestingDockerIO

# Copy only the necessary files from the host to the container
COPY StyleTTS2 /TestingDockerIO/StyleTTS2
COPY requirements.txt /TestingDockerIO

# Install Python dependencies
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Clone the Git LFS repository and move the Models directory
RUN git lfs clone https://huggingface.co/yl4579/StyleTTS2-LibriTTS && \
    mv StyleTTS2-LibriTTS/Models .
