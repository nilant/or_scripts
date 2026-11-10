#! /usr/bin/env python3

import argparse
import json
import pathlib

"""Merge the results of several directories into the first one.

Usage: ./merge.py DIR1 DIR2 [DIR3 ...]

For each json in DIR1, the json with the same name in the other directories
(if any) is merged into it. The files in DIR1 are overwritten.
"""


# merge the same-named json files of input_dirs[1:] into those of input_dirs[0]
def merge(args):
    for input in args.input_dirs[0].glob("*.json"):
        with open(input, "r") as f:
            j = json.load(f)

        # later directories win on duplicate keys (dict union)
        for dir in args.input_dirs[1:]:
            file = dir / input.name
            if file.exists():
                with open(file, "r") as f:
                    j2 = json.load(f)
                j = j | j2

        with open(input, "w") as f:
            json.dump(j, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dirs", nargs="+", type=pathlib.Path)
    parser.set_defaults(func=merge)

    args = parser.parse_args()

    args.func(args)
