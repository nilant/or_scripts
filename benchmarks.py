#! /usr/bin/env python3
import argparse
import pathlib
import subprocess
import sys
import tomllib

"""Run every configured executable on every instance in a directory.

Usage: ./benchmarks.py INPUT_DIR [--config FILE]

Reads the [benchmarks] section of the config: `execs` lists the binaries in
./bin to run, every other key is forwarded to them as `--key value`.
"""


# must be launched from the project root dir (binaries are looked up in ./bin)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=pathlib.Path, help="instances directory")
    parser.add_argument("--config", type=pathlib.Path, help="configuration file")

    args = parser.parse_args()

    # sanity checks on the input directory
    if not args.input_dir.exists():
        print("input_dir does not exist")
        sys.exit()

    if not args.input_dir.glob("**/*.json"):
        print("input_dir does not contains any instance")
        sys.exit()

    # config file: --config, else ./config.toml in the current directory
    if args.config:
        config_path = args.config
    elif pathlib.Path("config.toml").exists():
        config_path = pathlib.Path("config.toml")
    else:
        print("no configuration available")
        sys.exit()

    with open(config_path, "rb") as f:
        config = tomllib.load(f)["benchmarks"]

    execs = config["execs"]

    # every key except `execs` becomes a command line option for the binaries
    cmdl_args = []
    for k, v in config.items():
        if k != "execs":
            cmdl_args.append(f"--{k}")
            cmdl_args.append(str(v))

    # run each binary over all the instances, one after the other
    for cmd in execs:
        cmd = "./bin/" + cmd
        for input in args.input_dir.glob("**/*.json"):
            print(f"launching {cmd} with input {input}...")
            subprocess.run([cmd, input] + cmdl_args, check=False)
