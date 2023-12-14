MocapNET V4
===========

Original docs are in [README\_ORIGINAL.md](./README_ORIGINAL.md).

This is a snapshot of (branch `tag mnet4`). It was taken
from the official MocapNET repo at https://github.com/FORTH-ModelBasedTracker/MocapNET/tree/mnet4


Dev Installation
----------------

```sh
cd MocapNET/tree/mnet4/docker
bash build_and_deploy.sh
```

Usage
-----
```
Download a sample vid as a test: ```wget http://ammar.gr/mocapnet/shuffle.webm -O shuffle.webm```

Run: ``python3 -m mediapipeHolisticWebcamMocapNET --from shuffle.webm --ik 0.001 99 99 --smooth 60 10 --all --save --plot --headless 2``
```

```
Usage: python3 -m mediapipeHolisticWebcamMocapNET --from INPUT_VID_PATH [OPTIONS]

  Inference

Options:
**--headless**: Runs the script without displaying the live video output in a window. Useful when you don't need a GUI or are running on a headless server (Prolly need this enabled in out case).

**--live**: Activates a live demo mode. Specific functionality might change based on the script's implementation.

**--mt**: Stands for multi-threaded. This enables the script to run in a multi-threaded mode, potentially improving performance on multi-core processors.

**--calib [filename]**: Specifies a calibration file to use. Calibration files are used to adjust camera parameters or other settings.

**--frameskip [number]**: Skips a specified number of frames. Useful for reducing processing load or speeding up video processing.

**--nnsubsample [number]**: Specifies how often to run the neural network. For example, if set to 2, the NN will run on every second frame.

**--ik [float int int]**: Parameters for inverse kinematics (IK). The float might be a learning rate, followed by epochs and iterations, which control the IK optimization process.

**--smooth [float float]**: Sets parameters for smoothing, likely the sampling rate and cutoff frequency. This is used to smooth the motion capture data.

**--noik**: Disables the inverse kinematics processing.

**--aspectCorrection [float]**: Adjusts the aspect ratio of the input video or image stream.

**--noise [float]**: Adds a specified level of noise to the input data, possibly to test robustness or simulate less-than-ideal conditions.

**--size [int int]**: Sets the width and height of the video or image stream.

**--scale [float]**: Scales the output motion capture data.

**--plot**: Enables plotting of BVH (Biovision Hierarchy) channels, which might display skeletal animation or similar data.

**--all**: Activates all processing options (body, eyes, mouth, hands).

**--nobody**: Disables body joint estimation.

**--face**: Enables face joint estimation.

**--eyes / --reye**: Activates right eye joint estimation.

**--mouth**: Enables mouth joint estimation.

**--hands**: Activates hand joint estimation.

**--save**: Saves the output of the script. Depending on the script's functionality, this could mean saving processed video frames, motion capture data, or logs. In the context of this script, it seems to save the output images and possibly videos of the motion capture process.

**--engine [engine_name]**: Specifies the engine to be used, which could be different versions or types of neural network backends.

**--from [filepath]**: Defines the input source. This could be a file path to a video or a device path for live camera feed.

**--profile**: Possibly activates a profiling mode, which would gather performance metrics during script execution.
```
