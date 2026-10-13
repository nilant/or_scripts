#! /usr/bin/env python3

import pathlib
import argparse
import json

def merge(args):
    for input in args.input_dirs[0].glob('*.json'):
        with open(input, 'r') as f:
            j = json.load(f)
        
        for dir in args.input_dirs[1:]:
            file = dir / input.name
            if file.exists():
                with open(file, 'r') as f:
                    j2 = json.load(f)
                j = j | j2
        
        with open(input, 'w') as f:
            json.dump(j, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dirs', nargs='+', type=pathlib.Path) 
    parser.set_defaults(func=merge)

    args = parser.parse_args()

    args.func(args)
