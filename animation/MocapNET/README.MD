
# MocapNET V4
Welcome to the MocapNET V4 documentation! 🎉

🔗 **Original Documentation**: Find the original docs at [README_ORIGINAL.md](./README_ORIGINAL.md).

This snapshot from the `tag mnet4` branch is brought to you directly from the [official MocapNET repo](https://github.com/FORTH-ModelBasedTracker/MocapNET/tree/mnet4). Dive into the world of motion capture with ease!

## 🚀 Getting Started: Developer Installation

### For Linux Users

To install MocapNET V4 on a Linux system:

```sh
cd MocapNET/tree/mnet4/docker
bash build_and_deploy.sh
```

This script will build and run a Docker image, setting up the necessary environment for MocapNET V4.

### For Windows Users

For Windows users, using the Windows Subsystem for Linux (WSL) is recommended:

1. **Enable WSL on Windows**:
   - Open PowerShell as Administrator and run: 
     ```powershell
     dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
     ```
   - Restart your computer when prompted.

2. **Install a Linux Distribution from the Microsoft Store**:
   - Select and install your preferred Linux distribution (e.g., Ubuntu, Debian, Fedora).

3. **Set Up Your Linux Distribution**:
   - Launch the Linux distribution and follow the on-screen instructions to set up your account.

4. **Update and Upgrade Your Linux Distribution**:
   - Run: `sudo apt update && sudo apt upgrade`

5. **Install Docker on WSL**:
   - Follow the Docker installation instructions for your Linux distribution.

6. **Install MocapNET V4**:
   - Navigate to the `MocapNET/tree/mnet4/docker` directory.
   - Run the `build_and_deploy.sh` script.

For a detailed guide on setting up WSL, watch this YouTube tutorial: [How to Set Up WSL](https://www.youtube.com/watch?v=1HzYU2_t3yc)

## 🎬 How to Use

### Quick Start with a Sample Video
Get started by downloading a sample video:

```sh
wget http://ammar.gr/mocapnet/shuffle.webm -O shuffle.webm
```

### Run the Magic ✨
Execute this command:

```sh
python3 -m mediapipeHolisticWebcamMocapNET --from shuffle.webm --ik 0.001 99 99 --smooth 60 10 --all --save --plot --headless 2
```

### Convert the output bvh to generate bvh without face and toes bones
Execute this command:

```sh
./GroundTruthDumper --from dependencies/RGBDAcquisition/opengl_acquisition_shared_library/opengl_depth_and_color_renderer/Motions/DAZFriendlyCGSPEED_ZXYAndHandsAxisBigHands.bvh --merge src/python/mnet4/out.bvh dependencies/RGBDAcquisition/opengl_acquisition_shared_library/opengl_depth_and_color_renderer/Motions//mergeDazFriendlyAndAddHead.profile --setPositionRotation 0 0 0 0 0 0 --bvh remade.bvh
```

### Notes:

- The output bvh file will be stored inside this directory ``MocapNET/src/python/mnet4`` with the filename ``out.bvh``

- The converted bvh file will be stored in the root directory ``MocapNET`` with the filename ``remade.bvh``



### Command-Line Options Explained

- `--headless`: Skip the live video display. Ideal for headless servers or GUI-less environments.
- `--live`: Launches a live demo. Functionalities may vary.
- `--mt`: Enable multi-threading for better performance on multi-core CPUs.
- `--calib [filename]`: Use a specific calibration file for camera adjustments.
- `--frameskip [number]`: Skip a set number of frames to reduce load or speed up processing.
- `--nnsubsample [number]`: Run the neural network at set intervals (e.g., every 2nd frame).
- `--ik [float int int]`: Set parameters for inverse kinematics optimization.
- `--smooth [float float]`: Apply smoothing to motion capture data.
- `--noik`: Turn off inverse kinematics processing.
- `--aspectCorrection [float]`: Adjust video or image aspect ratio.
- `--noise [float]`: Add noise to input for testing under varied conditions.
- `--size [int int]`: Define video/image dimensions.
- `--scale [float]`: Scale the output motion data.
- `--plot`: Plot BVH channels for skeletal animation visualization.
- `--all`: Activate all processing features (body, eyes, mouth, hands).
- `--nobody`: Disable body joint estimation.
- `--face`: Enable face joint estimation.
- `--eyes / --reye`: Estimate right eye joints.
- `--mouth`: Enable mouth joint estimation.
- `--hands`: Estimate hand joints.
- `--save`: Save outputs (images, videos, data, logs).
- `--engine [engine_name]`: Choose a specific neural network backend.
- `--from [filepath]`: Specify input source (video file or live feed).
- `--profile`: Activate performance profiling.

## THIS README IS A W.I.P 
