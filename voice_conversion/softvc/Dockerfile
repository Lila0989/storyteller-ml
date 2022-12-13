
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# See: https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.title='Storyteller ML: Voice Conversion'
LABEL org.opencontainers.image.authors='bt@brand.io, echelon@gmail.com'
LABEL org.opencontainers.image.description='From the Storyteller ML model monorepo: TTS, etc.'
LABEL org.opencontainers.image.documentation='https://github.com/storytold/tts-core'
LABEL org.opencontainers.image.source='https://github.com/storytold/tts-core'
LABEL org.opencontainers.image.url='https://github.com/storytold/tts-core'

# tzdata install hangs without presetting the time zone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

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
        --no-install-recommends

# NB: Emit version for build debugging
RUN python3 --version

COPY requirements.txt .

# # NB: Forget about virtual environments inside the container.
# #   Also note the --extra-index-url, which is required for pytorch. 
# #   The version persisted to 'requirements.txt' chokes without it.
# RUN pip install --upgrade pip \
#     && pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116 \
#     && pip install -r requirements.txt

# NB: Install requirements in a virtual env too.
#   Also note the --extra-index-url, which is required for pytorch. 
#   The version persisted to 'requirements.txt' chokes without it.
RUN python3 -m venv python
RUN . python/bin/activate \
    && pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116 \
    && pip install -r requirements.txt \
    && deactivate

# Copy remaining files
COPY . ./
