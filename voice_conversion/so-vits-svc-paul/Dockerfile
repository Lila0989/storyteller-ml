FROM nvidia/cuda:12.0.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    nvidia-driver-515 \
    python3.10 \
    python3-pip \
    python3.10-venv \
    python3.10-dev \
    vim \
    curl \
    wget \
    htop \
    libsndfile1 \
    --no-install-recommends \
    && apt-get clean autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/




COPY . /models/voice_conversion/so-vits-svc

WORKDIR /models/voice_conversion/so-vits-svc
RUN pip install -e .
WORKDIR /
