#!/bin/bash

#python inference.py --cfg configs/Animate_X_infer.yaml

python inference_cli.py \
    --cfg configs/Animate_X_infer.yaml \
    --image_file data_test_copy/images/astronaut.jpg \
    --pose_directory data_test_copy/saved_pose/dance_1 \
    --frame_directory data_test_copy/saved_frames/dance_1 \
    --pickle_data_file data_test_copy/saved_pkl/dance_1.pkl \
    --width 768 \
    --height 512
