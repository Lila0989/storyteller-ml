# ==================== Python Build Base ====================

FROM ghcr.io/storytold/docker-base-images-nvidia-cuda-experimental:080f96bc7087 as pybuild-base

## Authenticating with GHCR locally:
## https://docs.github.com/en/packages/working-with-a-github-packages-registry/migrating-to-the-container-registry-from-the-docker-registry
##   ```
##   export CR_PAT=YOUR_TOKEN
##   echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
##   ```
#
##FROM nvidia/cuda:10.1-devel-ubuntu18.04 as pybuild-base
#FROM nvidia/cuda:11.3.0-devel-ubuntu20.04 as pybuild-base
#
## tzdata install hangs without presetting the time zone
#ENV TZ=UTC
#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
#
## NB(2021-05-30): This is the image that Tacotron 2's Dockerfile specifies.
## I have not tried this, but it might be necessary.
##FROM pytorch/pytorch:nightly-devel-cuda10.0-cudnn7
##ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
#
## NB: https://github.com/NVIDIA/nvidia-docker/issues/864#issuecomment-439848887
## NB: We do not install ffmpeg, since the version is 3.8.* series and we need 4.2.*
##
## NB(2021-05-30): We need to install `cython3` for building modern Tacotron 2
## dependencies (ie. protoc) on old Ubuntu
## RUN apt-get update \
##     && apt-get install -y \
#RUN apt-get update
##RUN apt-cache search python3.8
#
## NB: Here we install nvidia drivers
## NB: Avoid keyboard prompt
#RUN DEBIAN_FRONTEND=noninteractive apt-get install -y nvidia-384 --no-install-recommends
#
## ffmpeg version 4.2.4-1ubuntu0.1 Copyright (c) 2000-2020 the FFmpeg developers
##RUN apt-get install -y ffmpeg
##RUN ffmpeg -version
##RUN sleep 100
#
## Notes on packages:
##  * software-properties-common - needed for `apt-add-repository`
##  * pciutils - needed for `lspci | grep -i nvidia`
#RUN apt-get install -y \
#        build-essential \
#        curl \
#        cython3 \
#        ffmpeg \
#        g++-7 \
#        gcc-7 \
#        git \
#        htop \
#        imagemagick \
#        libc++-7-dev \
#        libffi-dev \
#        libgcc-7-dev \
#        libmagic1 \
#        libsm6 \
#        libsndfile1 \
#        libssl-dev \
#        libxext6 \
#        libxrender-dev \
#        netcat \
#        pciutils \
#        python-dev \
#        python3-pip \
#        python3.8 \
#        python3.8-dev \
#        python3.8-venv\
#        redis-tools \
#        silversearcher-ag \
#        software-properties-common \
#        sox \
#        tmux \
#        vim \
#        wget
#
#
## Wav2Lip needs Python3.6
## NB: we install python3-virtualenv as `python3.6 -m venv` won't work anymore
#RUN add-apt-repository ppa:deadsnakes/ppa
#RUN apt-get update
#RUN apt-get install -y python3.6
#RUN apt-get install -y python3-virtualenv
#RUN apt-get install -y python3.6-venv
#RUN apt-get install -y python3.6-dev
##RUN apt-get install python3-virtualenv
#
#
#RUN python3.6 --version
#RUN python3.8 --version

# We need ffmpeg version >= 4.2 (https://superuser.com/a/579110)
# http://ubuntuhandbook.org/index.php/2020/06/install-ffmpeg-4-3-via-ppa-ubuntu-18-04-16-04/

#RUN apt-get install -y software-properties-common \
#    && add-apt-repository ppa:jonathonf/ffmpeg-4 \
#    && apt-get update \
#    && apt-get install -y ffmpeg
#

# The downloader needs youtube-dl as a python library
# NB: No longer maintained: https://news.ycombinator.com/item?id=28319624
#RUN pip3 install --upgrade youtube-dl

# Used by the downloader script.
# And it looks like youtube-dl is dead...
# Per the README, it looks like pip will always pull the latest version.
# https://github.com/yt-dlp/yt-dlp#update
RUN python3 -m pip install --upgrade yt-dlp

# ==================== Tacotron, Waveglow, HifiGan, etc. ====================

FROM pybuild-base as pybuild-requirements

WORKDIR /

COPY ./tts ./models/tts
WORKDIR models/tts

# NB: Not sure if we need Python3.6 for Tacotron2, but Python3.8 gave me trouble.
# NB: Setuptools fix: https://github.com/tensorflow/tensorflow/issues/34302#issuecomment-554450289
RUN python3.6 -m venv python
RUN . python/bin/activate \
  && pip install --upgrade pip setuptools \
  && pip install -r requirements-tacotron-python36.txt \
  && deactivate



# Final image
#  FROM ubuntu:xenial
FROM pybuild-requirements as final
WORKDIR /

#COPY scripts/ ./scripts

# See: https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.authors='bt@brand.io, echelon@gmail.com'
LABEL org.opencontainers.image.url='https://github.com/storytold/tts-core'
LABEL org.opencontainers.image.documentation='https://github.com/storytold/tts-core'
LABEL org.opencontainers.image.source='https://github.com/storytold/tts-core'

# NB: Comment this out for non-debug images
# TODO: Figure out how this is done elsewhere with just the static binaries
# Others: `mysql-client`
RUN apt-get update \
    && apt-get install -y \
        curl \
        python3-pip \
        python3 \
        wget

RUN python3 --version
#RUN python3.7 -m venv python
#RUN . python/bin/activate \
#  && pip install --upgrade pip \
#  && pip install -r requirements.txt

# TODO: Use venv to do this instead.
RUN pip3 install gdown

