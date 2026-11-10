#! /usr/bin/env python3

import argparse
import json
import pathlib
import sys

"""Remove the results of the given algorithms from the instance JSON files.

Usage: ./clean.py INPUT_DIR --exec ALGO [ALGO ...]
"""


# delete the top-level key of each algorithm from every json under input_dir
def clean(args):
    if not args.input_dir.exists():
        print("input directory does not exists")
        sys.exit(1)
    for file in args.input_dir.glob("**/*.json"):
        # load the instance file
        with open(file, "r") as f:
            d = json.load(f)

        # drop the results of the selected algorithms, if present
        for key in args.exec:
            if key in d:
                del d[key]

        # write the file back in place
        with open(file, "w") as f:
            json.dump(d, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=pathlib.Path)
    parser.add_argument("--exec", nargs="+", help="algorithm name to clean")

    parser.set_defaults(func=clean)

    args = parser.parse_args()

    args.func(args)
