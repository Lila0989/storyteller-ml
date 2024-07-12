# Base CUDA image
FROM cnstark/pytorch:2.0.1-py3.9.17-cuda11.8.0-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Create directories for Python installation and model code
RUN mkdir /python_install
RUN mkdir -p /model_code/GPT-SoVITS

# Set the working directory for Python installation
WORKDIR /python_install

# Install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    ffmpeg \
    libsox-dev \
    parallel \
    aria2 \
    git \
    git-lfs \
    dos2unix \
    nano && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt and install Python dependencies
COPY requirements.txt /python_install/
RUN python3 -m venv python && \
    . /python_install/python/bin/activate && \
    python/bin/pip install --upgrade pip wheel setuptools && \
    python/bin/pip install --no-cache-dir -r requirements.txt

# Copy links.txt and links.sha256 to the appropriate directory
COPY Docker/links.txt /python_install/Docker/links.txt
COPY Docker/links.sha256 /python_install/Docker/links.sha256

# Download models directly using aria2c
RUN aria2c --disable-ipv6 --input-file /python_install/Docker/links.txt --dir /python_install --continue

# Verify the downloaded files using checksums
RUN cat /python_install/Docker/links.sha256 && ls -la /python_install/GPT_SoVITS/pretrained_models && \
    parallel --will-cite -a /python_install/Docker/links.sha256 "echo -n {} | sha256sum -c"

# Move Docker, GPT_SoVITS, requirements.txt, and tools to /model_code/GPT-SoVITS
RUN mv /python_install/Docker /model_code/GPT-SoVITS/ && \
    mv /python_install/GPT_SoVITS /model_code/GPT-SoVITS/ && \
    mv /python_install/requirements.txt /model_code/GPT-SoVITS/ && \
    mv /python_install/tools /model_code/GPT-SoVITS/

# Set the working directory for model code
WORKDIR /model_code/GPT-SoVITS

# Download additional models using modelscope
RUN /python_install/python/bin/pip install modelscope && \
    /python_install/python/bin/python -c "from modelscope import snapshot_download; snapshot_download('damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch', revision='v2.0.4');" && \
    /python_install/python/bin/python -c "from modelscope import snapshot_download; snapshot_download('damo/speech_fsmn_vad_zh-cn-16k-common-pytorch', revision='v2.0.4');" && \
    /python_install/python/bin/python -c "from modelscope import snapshot_download; snapshot_download('damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch', revision='v2.0.4');"

# Copy the remaining contents to the model_code directory
COPY . /model_code/GPT-SoVITS

# Change working directory to the project folder
WORKDIR /model_code/GPT-SoVITS

# Run an interactive shell by default and activate the virtual environment
CMD ["bash", "-c", ". /python_install/python/bin/activate && exec bash"]
