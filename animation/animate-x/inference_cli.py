#!/usr/bin/env python3

import argparse
import os

from utils.config import Config
from utils.registry_class import INFER_ENGINE

def parse_args():
    parser = argparse.ArgumentParser(
        description="Inference script",
        add_help=True
    )
    parser.add_argument(
        "--image_file",
        type=str,
        default=None,
        required=True
    )
    parser.add_argument(
        "--pose_directory",
        type=str,
        default=None,
        required=True
    )
    parser.add_argument(
        "--frame_directory",
        type=str,
        default=None,
        required=True
    )
    parser.add_argument(
        "--pickle_data_file",
        type=str,
        default=None,
        required=True
    )
    parser.add_argument(
        "--max_frames",
        type=int,
        default=None,
        required=False
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        required=False
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        required=False
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=14,
        required=False
    )
    #parser.add_argument(
    #    "--pretrained_model_name_or_path",
    #    type=str,
    #    default=None,
    #    required=True
    #)
    args, _unknown = parser.parse_known_args()
    return args


def main():
    args = parse_args()
    cfg_update = Config(load=True)

    # NB(bt,2025-02-04): Patching into their config-driven structure is super brittle. Be careful of updates.

    if not args.image_file or not os.path.isfile(args.image_file):
        raise Exception(f"Image file does not exist: #{args.image_file}")

    if not args.pose_directory or not os.path.isdir(args.pose_directory):
        raise Exception(f"Pose directory does not exist: #{args.pose_directory}")

    if not args.frame_directory or not os.path.isdir(args.frame_directory):
        raise Exception(f"Frame directory does not exist: #{args.frame_directory}")

    if not args.pickle_data_file or not os.path.isfile(args.pickle_data_file):
        raise Exception(f"Pickle data file does not exist: #{args.pickle_data_file}")

    cfg_update.cfg_dict['test_list_path'] = [[
        4, # ???
        args.image_file, 
        args.pose_directory,
        args.frame_directory,
        args.pickle_data_file,
        args.seed,
    ]]

    if args.max_frames:
        cfg_update.cfg_dict['max_frames'] = args.max_frames

    if args.width and args.height:
        cfg_update.cfg_dict['resolution'] = [args.width, args.height]

    print("Configurations:\n\n", cfg_update.cfg_dict, "\n\n")

    INFER_ENGINE.build(dict(type=cfg_update.TASK_TYPE), cfg_update=cfg_update.cfg_dict)


if __name__ == '__main__':
   main() 