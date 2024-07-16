# Base CUDA image
FROM cnstark/pytorch:2.0.1-py3.9.17-cuda11.8.0-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Create directories for Python installation and model code
RUN mkdir -p /python_install /model_code/GPT-SoVITS/GPT_SoVITS/pretrained_models

# Set the working directory for Python installation
WORKDIR /python_install

# Install necessary packages and git-lfs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    ffmpeg \
    libsox-dev \
    parallel \
    aria2 \
    git \
    dos2unix \
    nano \
    curl \
    software-properties-common \
    espeak-ng \
    sudo \
    rsync && \
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get install -y git-lfs && \
    git lfs install && \
    add-apt-repository ppa:deadsnakes/ppa && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt and install Python dependencies
COPY requirements.txt /python_install/
RUN python3 -m venv python && \
    . /python_install/python/bin/activate && \
    python/bin/pip install --upgrade pip wheel setuptools && \
    python/bin/pip install --no-cache-dir -r requirements.txt

# Clone Hugging Face repository and move models
RUN git clone https://huggingface.co/lj1995/GPT-SoVITS /python_install/GPT-SoVITS && \
    mkdir -p /model_code/GPT-SoVITS/GPT_SoVITS/pretrained_models && \
    mv /python_install/GPT-SoVITS/* /model_code/GPT-SoVITS/GPT_SoVITS/pretrained_models/

# Move Docker, GPT_SoVITS, requirements.txt, and tools to /model_code/GPT-SoVITS
RUN mv /python_install/requirements.txt /model_code/GPT-SoVITS/

# Set the working directory for model code
WORKDIR /model_code/GPT-SoVITS

# Copy the remaining contents to the model_code directory
COPY . /model_code/GPT-SoVITS

# Change working directory to the project folder
WORKDIR /model_code/GPT-SoVITS

# Run an interactive shell by default and activate the virtual environment
CMD ["bash", "-c", ". /python_install/python/bin/activate && exec bash"]
