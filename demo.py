#!/usr/bin/env python

###
# File: demo.py
# Created: Monday, 29th March 2021 5:51:52 pm
# Author: Andreas (amplejoe@gmail.com)
# -----
# Last Modified: Wednesday, 31st March 2021 3:57:48 am
# Modified By: Andreas (amplejoe@gmail.com)
# -----
# Copyright (c) 2021 Klagenfurt University
#
###

import argparse
import utils
import sys
import numpy as np
from tqdm import tqdm
import cv2
import ctypes
import os
from timeit import default_timer as timer
from collections import OrderedDict

# detectron2: https://github.com/facebookresearch/detectron2
from detectron2.data.datasets import register_coco_instances
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.utils.video_visualizer import VideoVisualizer
from detectron2.utils.visualizer import ColorMode, Visualizer

if os.name == "nt":
    ctypes.cdll.LoadLibrary("caffe2_nvrtc.dll")

# IN_EXTENSIONS = [".jpg", ".png"]

VID_EXT = [".mp4", ".avi"]
MODEL_EXT = [".pth"]
OUT_SUFFIX = "_out"
IN_CONFIGS = ".yaml"
PRED_CONF_THRESH = 0.5
OUT_SCALE = 1.2


def visualize_predictions(im, predictions):
    # annotate image with predictions
    v = Visualizer(im[:, :, ::-1], scale=OUT_SCALE)
    v = v.draw_instance_predictions(predictions["instances"].to("cpu"))
    pred_im = v.get_image()[:, :, ::-1]

    # scale original
    resized_im = utils.scale_image(pred_im, OUT_SCALE)
    return resized_im


def predict_video_generator(video, max_frames, predictor, visualizer, results):
    """Runs prediction on full video or until max_frames.
       Adapted from: https://stackoverflow.com/questions/60663073/how-can-i-properly-run-detectron2-on-videos

    Args:
        video ([type]): OpenCV video cap
        max_frames (int): maximum number of frames to predict
        predictor ([type]): d2 predictor (pre-initialized for performance)
        visualizer ([type]): d2 video visualizer (pre-initialized for performance)
        results ([OrderedDict]): overall results stored in a pass by reference variable

    Yields:
        [type]: [description]
    """

    cur_frame = 0
    while True:
        has_frame, frame = video.read()
        if not has_frame:
            break

        # prediction for frame
        start = timer()
        outputs = predictor(frame)
        end = timer()
        diff_ms = 1000 * (end - start)
        tqdm.write(f"prediction time: {diff_ms: .2f} ms")

        # make sure the frame is colored
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # frame visualization
        visualization = visualizer.draw_instance_predictions(
            frame, outputs["instances"].to("cpu")
        )

        # extract prediction stuff (uncomment if other fields are needed)
        # how to use 'instances': https://detectron2.readthedocs.io/en/latest/modules/structures.html#detectron2.structures.Instances
        if len(outputs["instances"]) > 0:
            results[cur_frame] = {
                # "image_size": outputs["instances"].image_size,
                # "total_frames": max_frames,
                "num_predictions": len(outputs["instances"]),
                "scores": outputs["instances"].scores.tolist(),
                # INFO: too much data for now
                # "pred_boxes": [x.tolist() for x in outputs["instances"].pred_boxes],
                # "pred_maskes": outputs["instances"].pred_masks.tolist(),
                "pred_classes": outputs["instances"].pred_classes.tolist(),
            }
            # DEBUG
            # tqdm.write(results[cur_frame])

        # convert Matplotlib RGB format to OpenCV BGR format
        visualization = cv2.cvtColor(visualization.get_image(), cv2.COLOR_RGB2BGR)
        yield visualization

        cur_frame += 1
        if cur_frame > max_frames:
            break


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
    if len(in_videos) == 0:
        utils.abort("No videos found.")
    if len(in_models) == 0:
        utils.abort("No models found.")
    if in_video_root == out_root:
        utils.abort("Input root cannot be the same as output root.")

    # overwrite existing out paths
    if not utils.confirm_delete_path(out_root, "n"):
        print(
            "Using existing output folder - finished analyzed videos will not be overwritten!"
        )

    # MODEL LOOP
    for model in tqdm(in_models, desc="models", position=2, leave=True):

        # get model config
        model_dir = utils.get_file_path(model)
        model_name = utils.get_file_name(model)
        configs = utils.get_files(model_dir, IN_CONFIGS)
        if len(configs) < 1:
            tqdm.write(
                f"No config file found in model folder, skipping model {model_name}"
            )
            continue
        config = configs[0]  # use 1st yaml file in model folder
        model_cfg = config
        tqdm.write(
            f"model: {utils.get_file_name(model, True)}, config: {utils.get_file_name(config, True)}"
        )

        # load config
        cfg = get_cfg()
        cfg.merge_from_file(model_cfg)  # detectron2 yaml file
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = (
            PRED_CONF_THRESH  # set threshold for this model
        )
        # set weights to path of 'pth' / 'pkl' files
        cfg.MODEL.WEIGHTS = model
        # predictor and visualizer
        predictor = DefaultPredictor(cfg)
        visualizer = VideoVisualizer(
            MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), ColorMode.IMAGE
        )

        # VIDEO LOOP
        for video in tqdm(in_videos, desc="videos", position=1, leave=True):
            # out paths
            video_name_full = utils.get_file_name(video, True)
            video_name = utils.get_file_name(video)
            video_ext = utils.get_file_ext(video)
            rel_video_folder = utils.get_file_path(
                utils.path_to_relative_path(video, in_video_root)
            )
            out_dir = utils.join_paths(out_root, rel_video_folder, video_name_full)
            out_video_file = utils.join_paths(
                out_dir, f"{model_name}{video_name}{video_ext}"
            )
            out_results_file = utils.join_paths(
                out_dir, f"{model_name}{video_name}.json"
            )
            if not utils.exists_dir(out_dir):
                utils.make_dir(out_dir)

            # is results file existing -> video has been fully analyzed, skip video
            if utils.exists_file(out_results_file):
                tqdm.write(
                    f"Result file already exists: {out_results_file}. Skipping video..."
                )
                continue
            elif utils.exists_file(out_video_file):
                tqdm.write(
                    f"Video file exists but results file is missing. Replacing video..."
                )
                utils.remove_file(out_video_file)

            # video and properties
            cap = cv2.VideoCapture(video)
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # video writer
            v_writer = cv2.VideoWriter(
                out_video_file,
                fourcc=cv2.VideoWriter_fourcc(*"mp4v"),
                fps=float(fps),
                frameSize=(w, h),
                isColor=True,
            )

            # DEBUG
            # num_frames = 100

            prediction_results = OrderedDict()
            vid_generator = predict_video_generator(
                cap, num_frames, predictor, visualizer, prediction_results
            )
            for visualization in tqdm(
                vid_generator, desc="frames", total=num_frames, position=0, leave=True
            ):

                # DEBUG: test image output
                # out_img_path = utils.join_paths(out_root, "test.png")
                # cv2.imwrite(out_img_path, visualization)

                # video file output
                v_writer.write(visualization)

            # cleanup
            cap.release()
            v_writer.release()
            cv2.destroyAllWindows()

            # output results
            out_data = OrderedDict(
                {
                    "height": h,
                    "width": w,
                    "num_frames": num_frames,
                    "predictions": prediction_results,
                }
            )
            utils.write_json(out_results_file, out_data)
            tqdm.write(f"Wrote {out_results_file}")

            # exec indicate_preds.py
            script_dir = utils.get_script_dir()
            indicatepredspy = utils.join_paths(script_dir, "indicate_preds.py")
            cmd_indicator = f"python {indicatepredspy} -v '{out_video_file}' -p '{out_results_file}'"
            utils.exec_shell_command(
                cmd_indicator,
                False,
            )
            print("After shell executed!!")


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
