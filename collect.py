#! /usr/bin/env python3

import argparse
import itertools
import json
import numbers
import pathlib
import sys
import tomllib

import pandas as pd

"""Collect the results of the instance JSON files into a single table.

Usage: ./collect.py INPUT_DIR [--config FILE] [--format csv|excel]

The table is written to ./doc/<INPUT_DIR name>.{csv,xlsx}. Columns and index
are selected by the [collect] section of the config.
"""


# flatten one json to a single-row dataframe with (section, field) columns;
# only numbers and strings are kept
def read_json(path):
    with open(path, "r") as f:
        try:
            d = json.load(f)
        except Exception:
            print(f"error reading file {f}")
            sys.exit(1)
        d = {
            (outer, inner): [d[outer][inner]]
            for outer in d
            for inner in d[outer]
            if isinstance(d[outer][inner], (numbers.Number, str))
        }
    return pd.DataFrame(d)


# read all the jsons under input_dir into one dataframe indexed by instance_index
def read_dataframe(args):
    list_of_df = [read_json(f) for f in args.input_dir.glob("**/*.json")]
    df = pd.concat(list_of_df)

    index = list(itertools.product(["instance"], config["instance_index"]))
    df = df.set_index(index).sort_index()
    df.index.names = config["instance_index"]
    return df


# select the configured columns and write the table to ./doc
def write_output(args):
    df = read_dataframe(args)

    # algorithm names without extension
    algos = [pathlib.Path(a).stem for a in config["execs"]]  # remove extension

    # keep only the configured instance and algorithm columns
    instaces_columns = list(itertools.product(["instance"], config["instance_fields"]))
    algos_columns = list(itertools.product(algos, config["exec_fields"]))

    df = df[instaces_columns + algos_columns]

    # output goes to ./doc/<input_dir name>.<ext>
    output_dir = pathlib.Path.cwd() / "doc"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / args.input_dir.name

    if args.format == "csv":
        df.to_csv(
            output_file.with_suffix(".csv"),
            na_rep="-",
            float_format="%.2f",
        )
    else:
        df.to_excel(
            output_file.with_suffix(".xlsx"),
            na_rep="-",
            float_format="%.2f",
            merge_cells=config["merge_cells"],
            sheet_name=args.input_dir.name,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=pathlib.Path)
    parser.add_argument("--config", type=pathlib.Path, help="configuration file")

    parser.add_argument(
        "--format",
        choices=["csv", "excel"],
        default="csv",
        help="output format (default: csv)",
    )

    parser.set_defaults(func=write_output)
    args = parser.parse_args()

    if args.config:
        config_path = args.config
    elif pathlib.Path("config.toml").exists():
        config_path = pathlib.Path("config.toml")
    else:
        print("no configuration available")
        sys.exit()

    with open(config_path, "rb") as f:
        config = tomllib.load(f)["collect"]

    args.func(args)
