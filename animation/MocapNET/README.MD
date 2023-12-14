# MocapNET V4
Welcome to the MocapNET V4 documentation! 🎉

🔗 **Original Documentation**: Find the original docs at [README_ORIGINAL.md](./README_ORIGINAL.md).

This snapshot from the `tag mnet4` branch is brought to you directly from the [official MocapNET repo](https://github.com/FORTH-ModelBasedTracker/MocapNET/tree/mnet4). Dive into the world of motion capture with ease!

## 🚀 Getting Started: Developer Installation

To get up and running with MocapNET V4, follow these simple steps:

```sh
cd MocapNET/tree/mnet4/docker
bash build_and_deploy.sh
```

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
