#!/usr/bin/env python

###
# File: demo.py
# Created: Monday, 29th March 2021 5:51:52 pm
# Author: Andreas (amplejoe@gmail.com)
# -----
# Last Modified: Saturday, 3rd April 2021 2:59:36 am
# Modified By: Andreas (amplejoe@gmail.com)
# -----
# Copyright (c) 2021 Klagenfurt University
#
###


from django_app.externals.apps.endo_seg import utils
from django_app.externals.apps.endo_seg.EndoSegPredictor import EndoSegPredictor

import argparse


VID_EXT = [".mp4", ".avi"]
MODEL_EXT = [".pth"]
OUT_SUFFIX = "_out"


def main():

    # in videos
    in_video_root = utils.get_file_path(g_args["in"])
    in_videos = [utils.to_path(g_args["in"])]
    if utils.exists_dir(g_args["in"]):
        # folder given as input - get videos
        in_video_root = utils.to_path(g_args["in"])
        in_videos = utils.get_files(in_video_root, *VID_EXT)
    # in models
    in_model_root = utils.get_file_path(g_args["model"])
    in_models = [utils.to_path(g_args["model"])]
    if utils.exists_dir(g_args["model"]):
        # folder given as input - get models
        in_model_root = utils.to_path(g_args["model"])
        in_models = utils.get_files(in_model_root, *MODEL_EXT)
    # out path
    out_root = f"{in_video_root}{OUT_SUFFIX}"
    if g_args["out"] is not None:
        out_root = utils.to_path(g_args["out"])

    # sanity checks
    if in_video_root == out_root:
        utils.abort("Input root cannot be the same as output root.")

    # predictions
    ep = EndoSegPredictor(
        videos=in_videos,
        models=in_models,
        video_root=in_video_root,
        output_root=out_root,
    )
    ep.run_predictions()


def parse_args():
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-i",
        "--in",
        type=str,
        help="path to video or input folder containing videos",
        required=True,
    )
    ap.add_argument(
        "-m",
        "--model",
        type=str,
        help="path to input model or root folder containing multiple model subfolders with their respectie config.yaml files",
        required=True,
    )
    ap.add_argument(
        "-o",
        "--out",
        type=str,
        help="path to output folder (default: [IN_PATH]_out)",
        required=False,
    )
    args = vars(ap.parse_args())
    return args


if __name__ == "__main__":
    # parse args
    g_args = parse_args()  # can be accessed globally
    # call main function
    main()
