#!/usr/bin/env python

###
# File: indicate_preds.py
# Created: Monday, 29th March 2021 5:51:52 pm
# Author: Andreas (amplejoe@gmail.com)
# -----
# Last Modified: Saturday, 3rd April 2021 3:07:29 am
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
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import cv2

OUT_SUFFIX = "_indicated"

COLORS = {
    "NONE": "white",
    "LOW": "#fed976",
    "MID_LOW": "#fd8d3c",
    "MID_HIGH": "#e31a1c",
    "HIGH": "#800026",
}

LOW = 0.5
MID_LOW = 0.625
MID_HIGH = 0.75
HIGH = 0.875

# test with: https://www.infobyip.com/detectmonitordpi.php
MONITOR_DPI = 120

BAR_HEIGHT_PX = 50

FULL_PLOT = False


def get_color(val):
    val_desc = "HIGH"
    if val < LOW:
        val_desc = "NONE"
    elif val < MID_LOW:
        val_desc = "LOW"
    elif val < MID_HIGH:
        val_desc = "MID_LOW"
    elif val < HIGH:
        val_desc = "MID_HIGH"

    # DEBUG
    # print(f"{val} - {val_desc} - {COLORS[val_desc]}")

    return COLORS[val_desc]


def get_score_avgs(preds):
    res_list = [0 for x in range(0, g_args["total_frames"])]
    for i, el in enumerate(res_list):
        i_str = str(i)
        if str(i_str) in preds.keys():
            val = sum(preds[i_str]["scores"]) / preds[i_str]["num_predictions"]
            res_list[i] = val

    # non sparse lists
    # val_lists = [v["scores"] for k, v in preds.items()]
    # val_list_avgs = [sum(l) / len(l) for l in val_lists]
    return res_list


def get_frames():
    return [x for x in range(0, g_args["total_frames"])]


def get_color_list(avg_list):
    return [get_color(x) for x in avg_list]


def resize_plot(w, h):
    plt.figure(figsize=(w / MONITOR_DPI, h / MONITOR_DPI), dpi=MONITOR_DPI)


def save_plot(path):
    plt.savefig(path, dpi=MONITOR_DPI)
    # plt.savefig(path, bbox_inches="tight", pad_inches=pad_inches, dpi=MONITOR_DPI)
    print(f"Wrote {path}")


def apply_conditional_fill(x_data, y_data):
    plt.fill_between(
        x_data,
        y_data,
        where=np.logical_and(y_data >= LOW, y_data < MID_LOW),
        color=get_color(LOW),
    )
    plt.fill_between(
        x_data,
        y_data,
        where=np.logical_and(y_data >= MID_LOW, y_data < MID_HIGH),
        color=get_color(MID_LOW),
    )
    plt.fill_between(
        x_data,
        y_data,
        where=np.logical_and(y_data >= MID_HIGH, y_data < HIGH),
        color=get_color(MID_HIGH),
    )
    plt.fill_between(x_data, y_data, where=(y_data >= HIGH), color=get_color(HIGH))


def plot_predictions(preds, out_path, *, width=800, height=600, remove_ticks=False):

    resize_plot(int(width), int(height))

    # frame_list = list(preds.keys()
    frame_list = get_frames()
    val_list_avgs = get_score_avgs(preds)
    colors = get_color_list(val_list_avgs)
    # print("vall")
    # print(val_list_avgs)
    # exit(list(preds.keys()))
    data_plot = pd.DataFrame(
        {"frame": frame_list, "score": val_list_avgs, "color": colors}
    )
    plt.xlim(0, g_args["total_frames"])
    plt.ylim(0.0, 1.0)

    # bar
    # sns.barplot(x="frame", y="score", data=data_plot)
    # line (simple)
    # sns.lineplot(x="frame", y="score", data=data_plot)

    # fill AUC
    # plt.fill_between(data_plot.frame.values, data_plot.score.values, color=cl)
    # plt.stackplot(data_plot["frame"], data_plot["score"], alpha=0.5) # alternative

    # line (colored)
    for i in tqdm(
        range(0, len(frame_list) - 1),
        desc=f"creating plot - {utils.get_file_name(out_path)}",
    ):
        frame_from_to = frame_list[i : i + 2]
        val_from_to = val_list_avgs[i : i + 2]
        cl = colors[i + 1]  # uphill
        if val_from_to[1] < val_from_to[0]:
            cl = colors[i]  # downhill

        apply_conditional_fill(data_plot.frame.values, data_plot.score.values)

        sns.lineplot(
            x=frame_from_to,
            y=val_from_to,
            color=cl,
        )

    plt.xticks(rotation=30)

    # plt.show()

    # OUTPUT

    if remove_ticks:
        plt.tick_params(
            axis="both",  # changes apply to the x-axis
            which="both",  # both major and minor ticks are affected
            top=False,  # ticks along the top edge are off
            right=False,  # ticks along the right edge are off
            bottom=False,  # ticks along the bottom edge are off
            left=False,  # ticks along the left edge are off
            labelbottom=False,
            labelleft=False,
        )
        plt.subplots_adjust(top=1, bottom=0.03, right=0.998, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)

    save_plot(out_path)

    # clean up
    plt.clf()


def input_check(in_var):
    if not utils.exists_file(in_var):
        exit(f"Input file not found: {in_var}")


def main():

    g_args["predictions"] = utils.to_path(g_args["predictions"])
    g_args["video"] = utils.to_path(g_args["video"])
    input_check(g_args["predictions"])
    input_check(g_args["video"])
    g_args["out_root"] = utils.get_file_path(g_args["predictions"])

    g_args["in_json"] = utils.read_json(g_args["predictions"])
    in_predictions = g_args["in_json"]["predictions"]
    g_args["total_frames"] = g_args["in_json"]["num_frames"]

    # print(in_predictions)
    # print(utils.add_suffix_to_file(g_args["video"], OUT_SUFFIX))
    # exit()

    # create result indicator bar

    # full
    if FULL_PLOT:
        full_plot_out = utils.join_paths(
            g_args["out_root"],
            f"{utils.get_file_name(g_args['predictions'])}_pred_plot.png",
        )
        plot_predictions(
            in_predictions,
            full_plot_out,
            width=int(g_args["in_json"]["width"]),
            height=int(g_args["in_json"]["height"]),
        )

    # bar only
    video_bar_out = utils.join_paths(
        g_args["out_root"],
        f"{utils.get_file_name(g_args['predictions'])}_bar.png",
    )
    plot_predictions(
        in_predictions,
        video_bar_out,
        width=int(g_args["in_json"]["width"]),
        height=BAR_HEIGHT_PX,
        remove_ticks=True,
    )

    # add indication to video
    out_video_file = utils.add_suffix_to_file(g_args["video"], OUT_SUFFIX)
    bar_image = utils.get_image(video_bar_out)

    # video and properties
    cap = cv2.VideoCapture(g_args["video"])
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # video writer
    v_writer = cv2.VideoWriter(
        out_video_file,
        fourcc=cv2.VideoWriter_fourcc(*'avc1'),
        fps=float(fps),
        frameSize=(w, h + BAR_HEIGHT_PX),
        isColor=True,
    )

    print("Creating indicator video...")
    cur_frame = 0
    pbar = tqdm(total=num_frames, desc="Progress")
    while True:
        has_frame, frame = cap.read()
        if not has_frame:
            break
        pbar.n = cur_frame + 1  # update pbar
        pbar.refresh()
        # paint current location indicator (horizontal line)
        cur_bar_image = utils.draw_horizontal_line(
            bar_image, x_pos_percent=(cur_frame + 1) / num_frames, line_thickness=2
        )
        res = utils.concatenate_images(frame, cur_bar_image, axis=0)
        # convert result to BGR
        res = cv2.cvtColor(res, cv2.COLOR_BGRA2BGR)
        # DEBUG
        # utils.show_image(res, "result")
        v_writer.write(res)
        cur_frame += 1
    print(f"Wrote {out_video_file}")

    # cleanup
    cap.release()
    v_writer.release()


def exit(msg=None):
    if msg:
        print(f"{msg}")
    print("Exit script.")
    sys.exit()


def parse_args():
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-p",
        "--predictions",
        type=str,
        help="path to input predictions json",
        required=True,
    )
    ap.add_argument(
        "-v",
        "--video",
        type=str,
        help=f"path to input video (output is created with {OUT_SUFFIX})",
        required=True,
    )

    args = vars(ap.parse_args())
    return args


if __name__ == "__main__":
    # parse args
    g_args = parse_args()  # can be accessed globally
    # call main function
    main()
