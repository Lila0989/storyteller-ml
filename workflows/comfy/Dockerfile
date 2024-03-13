
# NB(bt, 2022-12-12): The version of containerized CUDA must match (or be less than?) that of the host system running this container.
#  Juggling these dependencies, plus the underlying Ubuntu system (which controls Python versions), is tricky.
#  Nvidia does not provide a CUDA 11.6 with Ubuntu 22.04, which mirrors my own desktop machine. Their CUDA 11.6 + Ubuntu 20.04 image has
#  a stale Python (3.8), so we have to use the DeadSnakes PPA to install a more modern version.
#  Gross.
FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# See: https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.title='Storyteller ML: Voice Conversion'
LABEL org.opencontainers.image.authors='adrien@storyteller.ai'

# tzdata install hangs without presetting the time zone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Needed to install "future" release of Python 3.10 under Ubuntu 20.04, which only natively packages Python 3.8.
# We seem to be stuck on Ubuntu 22.04 because containerizd CUDA 11.6 is the only version we can run on my host machine,
# and Nvidia does not supply a (CUDA 11.6, Ubuntu 22.04) docker base image.
RUN apt-get update \
    && apt install software-properties-common -y \
    && add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
        curl \
        ffmpeg \
        libmagic-dev \
        libmagic1 \
        python3-pip \
        python3.10 \
        python3.10-venv \
        unzip \
        wget \
        git \
        --no-install-recommends

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
# Copy files to container
COPY --chown=appuser:appgroup initialize_comfy_extensions.py /app/initialize_comfy_extensions.py
COPY --chown=appuser:appgroup install.py /app/install.py
COPY --chown=appuser:appgroup repos.json /app/repos.json
COPY --chown=appuser:appgroup ComfyLauncher /app/ComfyLauncher
COPY --chown=appuser:appgroup format_video.py /app/format_video.py
COPY --chown=appuser:appgroup required_requirements.txt /app/required_requirements.txt
COPY --chown=appuser:appgroup dependencies.json /app/dependencies.json

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel requests argparse

RUN chmod -R 777 /app

# protobuf use python implementation (weird error without)
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
