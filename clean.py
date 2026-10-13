#! /usr/bin/env python3

import pathlib
import argparse
import sys
import json

# remove results 
def clean(args):
    if not args.input_dir.exists():
        print('input directory does not exists')
        sys.exit(1)
    for file in args.input_dir.glob('**/*.json'):
        with open(file, 'r') as f:
            d = json.load(f)

        for key in args.exec:
            if key in d:
                del d[key]

        with open(file, 'w') as f:
            json.dump(d, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=pathlib.Path) 
    parser.add_argument('--exec', nargs='+', help='algorithm name to clean')

    parser.set_defaults(func=clean)

    args = parser.parse_args()

    args.func(args)
