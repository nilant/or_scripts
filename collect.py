#! /usr/bin/env python3

import pandas as pd
import itertools
import sys
import argparse
import tomllib
import pathlib
import numbers
import json


def read_json(path):
    with open(path, 'r') as f:
        try:
            d = json.load(f)
        except Exception:
            print(f'error reading file {f}')
            exit(1)
        d = {(outer, inner): [d[outer][inner]] 
                            for outer in d.keys() for inner in d[outer].keys() 
                            if isinstance(d[outer][inner], numbers.Number) or
                               isinstance(d[outer][inner], str)}
    return pd.DataFrame(d) 

def read_dataframe(args):
    list_of_df = [read_json(f) for f in args.input_dir.glob('**/*.json')]
    df = pd.concat(list_of_df)

    index = list(itertools.product(['instance'], config['instance_index']))
    df = df.set_index(index).sort_index()
    df.index.names = config['instance_index']
    return df

def write_excel(args):
    df = read_dataframe(args)

    algos  = [pathlib.Path(a).stem for a in config['execs']]  # remove extension

    instaces_columns = list(itertools.product(['instance'], config['instance_fields']))
    algos_columns = list(itertools.product(algos, config['exec_fields']))

    df = df[instaces_columns + algos_columns]
    
    output_dir = pathlib.Path.cwd() / 'doc'
    output_dir.mkdir(exist_ok=True) 
    output_file = (output_dir / args.input_dir.name).with_suffix('.xlsx')

    df.to_excel(output_file, na_rep='-', float_format='%.2f', merge_cells=config['merge_cells'], sheet_name=args.input_dir.name)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=pathlib.Path) 
    parser.add_argument('--config', type=pathlib.Path, help='configuration file')

    parser.set_defaults(func=write_excel)
    args = parser.parse_args()

    if args.config:
        config_path = args.config
    elif pathlib.Path('config.toml').exists():
        config_path = pathlib.Path('config.toml')
    else:
        print('no configuration available')
        sys.exit()
    
    with open(config_path, 'rb') as f:
        config = tomllib.load(f)['collect']

    args.func(args)
