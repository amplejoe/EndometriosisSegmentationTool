#!/usr/bin/env python

###
# File: utils.py
# Created: Tuesday, 30th March 2021 2:10:16 am
# Author: Andreas (amplejoe@gmail.com)
# -----
# Last Modified: Tuesday, 30th March 2021 3:53:58 am
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
