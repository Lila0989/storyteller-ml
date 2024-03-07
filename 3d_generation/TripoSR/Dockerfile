FROM nvidia/cuda:11.8.0-devel-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1
ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6"
ENV TCNN_CUDA_ARCHITECTURES=86;80;75;70;61;60
ENV FORCE_CUDA=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
ENV LIBRARY_PATH=${CUDA_HOME}/lib64/stubs:${LIBRARY_PATH}

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libegl1-mesa-dev \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    python-is-python3 \
    python3-dev \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

ENV HOME=/root
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=$HOME/app
ENV GRADIO_ALLOW_FLAGGING=never
ENV GRADIO_NUM_PORTS=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_THEME=huggingface
ENV SYSTEM=spaces

RUN pip install --upgrade pip setuptools ninja
RUN pip install torch==2.2.1 --extra-index-url https://download.pytorch.org/whl/cu118

RUN python -c "import torch; print(torch.version.cuda)"
COPY requirements.txt /tmp/
RUN cd /tmp && pip install -r requirements.txt

# Set the working directory
WORKDIR /root/app

# Copy the current directory contents into the container at /root/app
COPY . /root/app