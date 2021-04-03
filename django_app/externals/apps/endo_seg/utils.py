#!/usr/bin/env python

###
# File: utils.py
# Created: Tuesday, 30th March 2021 2:10:16 am
# Author: Andreas (amplejoe@gmail.com)
# -----
# Last Modified: Wednesday, 31st March 2021 3:16:25 am
# Modified By: Andreas (amplejoe@gmail.com)
# -----
# Copyright (c) 2021 Klagenfurt University
#
###


## IMPORTS
import pathlib
import os
import sys
import errno
import shutil
import subprocess
import re
import cv2
import numpy as np
import json, simplejson
import inspect


def to_path(*p, as_string=True):
    """Convert string to pathlib path.
    INFO: Path resolving removes stuff like ".." with 'strict=False' the
    path is resolved as far as possible -- any remainder is appended
    without checking whether it really exists.
    """
    pl_path = pathlib.Path(*p)
    ret = pl_path.resolve(strict=False)  # default return in case it is absolute path

    if not pl_path.is_absolute():
        # don't resolve relative paths (pathlib makes them absolute otherwise)
        ret = pl_path

    if as_string:
        return ret.as_posix()
    else:
        return ret


def join_paths(path, *paths, as_string=True):
    """Joins path with arbitrary amount of other paths."""
    joined = to_path(path, as_string=False).joinpath(to_path(*paths, as_string=False))
    joined_resolved = to_path(joined, as_string=False)
    if as_string:
        return joined_resolved.as_posix()
    else:
        return joined_resolved


def path_to_relative_path(path, relative_to_path):
    """Return sub-path relative to input path"""
    path = to_path(path, as_string=False)
    rel_to = to_path(relative_to_path, as_string=False)
    return path.relative_to(rel_to).as_posix()


def exists_dir(*p):
    """Checks whether a directory really exists."""
    return to_path(*p, as_string=False).is_dir()


def exists_file(*p):
    """Checks whether a file really exists."""
    return to_path(*p, as_string=False).is_file()


def get_file_path(file_path):
    """file path only (strips file from its path)"""
    p = to_path(file_path, as_string=False)
    return p.parents[0].as_posix()


def get_files(directory, *extensions):
    """Get all file paths of a directory (optionally with file extensions
    usage example: get_file_paths("/mnt/mydir", ".json", ".jpg")
    changes:
        - 2019: using pathlib (python3) now
    """
    d = to_path(directory, as_string=False)

    all_files = []
    for current_file in d.glob("**/*"):
        if not current_file.is_file():
            continue
        fext = current_file.suffix
        if extensions and fext not in extensions:
            continue
        # as_posix: Return a string representation
        # of the path with forward slashes (/)
        all_files.append(current_file.as_posix())
    return all_files


def make_dir(path, show_info=False, overwrite=False):
    """Creates a directory
    Parameters
    ----------
    path:
        the directory path
    overwrite:
        force directory overwrite (default=False)
    show_info:
        show creation user infos (default=False)
    """
    try:
        if overwrite:
            remove_dir(path)
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Unexpected error: %s", str(e.errno))
            raise  # This was not a "directory exists" error..
        # print("Directory exists: %s", path)
        return False
    if show_info:
        print(f"Created dir: {path}")
    return True


def remove_dir(path):
    if exists_dir(path):
        # os.rmdir(path) # does not work if not empty
        shutil.rmtree(path, ignore_errors=True)  # ignore errors on windows


def remove_file(path):
    """Removes file (unlink) if existing.

    Args:
        path (string): file path
    """
    p = to_path(path, as_string=False)
    if exists_file(p):
        p.unlink()


def get_script_dir():
    """Returns directory of currently running script (i.e. calling file of this method)."""
    # starting from 0, every file has their own frame, take the second to last's file name (= calling file frame)
    calling_file = inspect.stack()[1][1]  # [frame idx] [file name]
    # return directory of calling file
    return os.path.dirname(os.path.abspath(calling_file))


def confirm(msg=None, default=None):
    """
    Ask user to enter Y or N (case-insensitive).
    :return: True if the answer is Y.
    :rtype: bool
    """
    if default != None:
        default = default.lower()
    accepted_answers = ["y", "n"]
    user_prompt = "[y/n]"
    if default is not None and default in accepted_answers:
        default = default.lower()
        accepted_answers.append("")  # allows users to press enter
        user_prompt = user_prompt.replace(default, default.upper())
    if msg is not None:
        print(msg)
    answer = None
    while answer not in accepted_answers:
        answer = input(user_prompt).lower()
        if answer == "":
            answer = default
    return answer == "y"


def confirm_delete_path(path, default=None):
    p = to_path(path, as_string=False)
    if p.is_dir():
        if confirm("Path exists: %s, delete folder?" % (path), default):
            remove_dir(path)
        else:
            # user explicitly typed 'n'
            return False
    return True


def abort(msg=None):
    """Exits script with optional message."""
    if msg:
        print(f"{msg}")
    print("Exit script.")
    sys.exit()


def get_file_name(file_path, full=False):
    """Get file name of file"""
    if full:
        return to_path(file_path, as_string=False).name
    else:
        return to_path(file_path, as_string=False).stem


def get_file_ext(file_path):
    """Get file extension of file (always with '.', i.e. 'test.jpg' -> '.jpg')"""
    return to_path(file_path, as_string=False).suffix


def add_suffix_to_file(file_path, suffix):
    """Adds a suffix to file path. No additional character is added, i.e. '_' needs to be part of suffix if required.

    Args:
        file_path ([type]): [description]
        suffix ([type]): The suffix. E.g. "_suffix"

    Returns:
        [type]: [description]
    """
    fp = get_file_path(file_path)
    fn = get_file_name(file_path)
    fe = get_file_ext(file_path)
    return join_paths(fp, f"{fn}{suffix}{fe}")

def exec_shell_command(command, print_output=False):
    """Executes a shell command using the subprocess module.
    command: standard shell command (SPACE separated - escape paths with '' or "")
    print_output: output command result to console
    returns: list containing all shell output lines
    """
    print(f"Exec shell command '{command}'")
    regex = r"[^\s\"']+|\"([^\"]*)\"|'([^']*)'"
    command_list = get_regex_match_list(command, regex)

    process = subprocess.Popen(
        command_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    output = []
    # execute reading output line by line
    for line in iter(process.stdout.readline, b""):
        line = line.decode(sys.stdout.encoding)
        output.append(line.replace("\n", ""))
        if print_output:
            sys.stdout.write(line)
    return output


def get_regex_match_list(in_string, regex):
    matches = re.finditer(regex, in_string)
    match_list = []
    for matchNum, match in enumerate(matches, start=1):
        match_list.append(match.group().strip("'").strip('"'))
    return match_list


def read_json(path, silent=True):
    """Loads a json file into a variable.
    Parameters:
    ----------
    path : str
        path to json file
    Return : dict
        dict containing all json fields and attributes
    """
    data = None
    try:
        with open(path) as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        if not silent:
            print(f"File not found: {path}")
    return data


def write_json(path, data, pretty_print=False, handle_nan=False):
    """Writes a json dict variable to a file.
    Parameters:
    ----------
    path : str
        path to json output file
    data : dict
        data compliant with json format
    """
    with open(path, "w", newline="") as outfile:
        if pretty_print:
            # OLD
            # json.dump(data, outfile, indent=4)
            # json.dump(data, outfile, indent=4, sort_keys=True)
            simplejson.dump(data, outfile, indent=4, ignore_nan=handle_nan)
        else:
            # OLD
            # json.dump(data, outfile)
            simplejson.dump(data, outfile, ignore_nan=handle_nan)


# opencv helper functions


def is_image(variable):
    # openCV images are numpy arrays (TODO: more thorough check)
    return type(variable) is np.ndarray


def get_image(path_or_image):
    """Returns an OpenCV image, whether a path or an image is provided.
    Ensures that most methods can be used by passing the image path OR the image itself.
    Parameters:
    -----------
    path_or_image: string or openCV image object
        path or OpenCV image
    returns:
        loaded OpenCV image
        (path_or_image if it already is an OpenCV image,
         a newly loaded one otherwise)

    """
    if is_image(path_or_image):
        return path_or_image
    else:
        # path must have been provided (TODO: error handling)
        return cv2.imread(path_or_image)


def draw_horizontal_line(img, x_pos_percent=0.5, line_thickness=1, color=(0, 255, 0)):
    """Draws a horizontal line through an input picture. position is given as a percentage.

    Args:
        img ([type]): [description]
        x_pos_percent ([type]): percentage of width, default 0.50
        color (tuple, optional): [description]. Defaults to (0,255,0).
    """
    img = get_image(img)
    img_altered = img.copy()
    width, height = img.shape[1], img.shape[0]
    x1, y1 = int(width * x_pos_percent), 0
    x2, y2 = int(width * x_pos_percent), height
    cv2.line(img_altered, (x1, y1), (x2, y2), (0, 255, 0), thickness=line_thickness)
    return img_altered


def scale_image(img, scale_factor, interpolation=cv2.INTER_AREA):
    width = int(img.shape[1] * scale_factor)
    height = int(img.shape[0] * scale_factor)
    dim = (width, height)
    resized_img = cv2.resize(img, dim, interpolation)
    return resized_img


def concatenate_images(img1, img2, axis=1):
    """Concatanates two images horizontally (axis=1, default) or vertically(axis=0).
    INPORTANT: outputs BGRA image, convert if other format needed!
    Parameters
    ----------
    img1: path or image
    img2: path or image
    """
    img1 = get_image(img1)
    img2 = get_image(img2)
    # ensure that dimensions match, by converting all imgs to RGBA
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2BGRA)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2BGRA)
    return np.concatenate((img1, img2), axis=axis)


def show_image(image, title, pos=None, destroy_after_keypress=True):
    """Shows image with option to set position and enabling ESCAPE to quit.
    Parameters:
    -----------
    image: object or path
        OpenCv image
    title: string
        window title
    pos: dict of integers
        {"x": x_pos, "y": y_pos}
    """
    image = get_image(image)
    cv2.imshow(title, image)
    if pos is not None:
        cv2.moveWindow(title, pos["x"], pos["y"])
    key = cv2.waitKey(0)
    if key == 27:
        sys.exit()
    if destroy_after_keypress:
        cv2.destroyWindow(title)  # cleanup