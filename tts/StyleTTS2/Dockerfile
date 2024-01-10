# Use ubuntu as the base image from the hub
# then have to build this as a image.
FROM nvidia/cuda:12.2.0-devel-ubuntu20.04
# Optional: Set environment variables
ENV MY_ENV_VARIABLE=value
ENV DEBIAN_FRONTEND=noninteractive
# Optional: Run commands to set up the image
RUN apt-get update && apt-get install -y curl

    # Preconfigure package selections (as an example)
RUN echo "package-name package-name/some-option select option-value" | debconf-set-selections && \ 
    apt-get install -y software-properties-common
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python3.10 -y
RUN apt-get install -y git
RUN sudo apt install ffmpeg
RUN sudo apt-get install espeak-ng
# Clone the repository

# RUN pwd
RUN pip3 install requirements.txt

# Navigate to the cloned directory
WORKDIR TestingDockerIO
COPY styletts2 . 



# # Allow parameters to be passed
ENTRYPOINT ["python3", "fakeyou_infer.py"]