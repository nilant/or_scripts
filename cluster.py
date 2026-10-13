#!/usr/bin/env python3

import argparse
import pathlib
import readline
import subprocess
import sys
import time
import tomllib


def deploy(remote_dir, minipcs):
    for pc in minipcs:
        subprocess.run(
            ["scp", "-r", "bin", "benchmarks.py", "configs", f"{pc}:{remote_dir}"]
        )
        subprocess.run(["ssh", pc, "mkdir", "-p", f"{remote_dir}/data"])


def collect(remote_dir, data_dir, minipcs):
    results_dir = f"{data_dir}_{time.strftime('%Y%m%d')}"
    subprocess.run(["mkdir", "-p", results_dir])
    for pc in minipcs:
        subprocess.run(["scp", "-r", f"{pc}:{remote_dir}/data/*", results_dir])
    # subprocess.run(['zip', '-r', f'{results_dir}.zip', results_dir])


def clean(remote_dir, minipcs):
    for pc in minipcs:
        subprocess.run(["ssh", pc, "rm", "-rf", f"{remote_dir}/*"])


def clean_data(remote_dir, minipcs):
    for pc in minipcs:
        subprocess.run(["ssh", pc, "rm", "-rf", f"{remote_dir}/data/*"])


def ls(remote_dir, minipcs):
    for pc in minipcs:
        print(f"{pc}")
        subprocess.run(["ssh", pc, "ls", f"{remote_dir}/*"])
        print("---------------------------")


def data(remote_dir, data_dir, minipcs):
    data_path = pathlib.Path(data_dir)
    files = data_path.glob("**/*.json")

    i = 0
    for file in files:
        subprocess.run(["scp", str(file), f"{minipcs[i]}:{remote_dir}/data"])
        i = (i + 1) % len(minipcs)


def ps(minipcs):
    for pc in minipcs:
        print(f"{pc}:")
        subprocess.run(["ssh", pc, "ps aux --sort=-pcpu | head -n 2"])


def run(remote_dir, minipcs):
    for pc in minipcs:
        subprocess.Popen(
            [
                "ssh",
                pc,
                f"cd {remote_dir} && nohup ./benchmarks.py data &>/dev/null </dev/null",
            ]
        )
    time.sleep(1)


def all_(remote_dir, data_dir, minipcs):
    clean(remote_dir, minipcs)
    deploy(remote_dir, minipcs)
    data(remote_dir, data_dir, minipcs)
    run(remote_dir, minipcs)


def load_config(config_path):
    if config_path:
        path = config_path
    elif pathlib.Path("config.toml").exists():
        path = pathlib.Path("config.toml")
    else:
        raise ValueError("no configuration available")

    with open(path, "rb") as f:
        config = tomllib.load(f)["cluster"]

    indices = config["indices"]
    remote_dir = config["remote_dir"]
    data_dir = "data/" + config["data_dir"]

    if len(indices) == 0:
        raise ValueError("no minipc specified")

    if remote_dir == "":
        raise ValueError("no remote dir specified")

    minipcs = ["minipc" + str(i) for i in indices]
    return remote_dir, data_dir, minipcs


# each command takes (remote_dir, data_dir, minipcs)
COMMANDS = {
    "deploy": lambda r, d, m: deploy(r, m),
    "collect": lambda r, d, m: collect(r, d, m),
    "clean": lambda r, d, m: clean(r, m),
    "clean_data": lambda r, d, m: clean_data(r, m),
    "ls": lambda r, d, m: ls(r, m),
    "data": lambda r, d, m: data(r, d, m),
    "ps": lambda r, d, m: ps(m),
    "run": lambda r, d, m: run(r, m),
    "all": all_,
}


def execute(command, settings):
    if command not in COMMANDS:
        print(f"unknown command: {command}")
        return
    try:
        COMMANDS[command](*settings)
    except KeyboardInterrupt:
        print()


def shell(config_path):
    settings = load_config(config_path)
    names = sorted(COMMANDS) + ["help", "reload", "quit", "exit"]

    readline.set_completer(
        lambda text, n: ([c for c in names if c.startswith(text)] + [None])[n]
    )
    readline.parse_and_bind("tab: complete")

    while True:
        try:
            line = input("cluster> ").strip()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue

        if not line:
            continue
        if line in ("quit", "exit"):
            break
        if line == "help":
            print("commands:", ", ".join(names))
        elif line == "reload":
            try:
                settings = load_config(config_path)
                print("configuration reloaded")
            except (ValueError, OSError, KeyError) as e:
                print(f"reload failed: {e}")
        else:
            execute(line, settings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", nargs="?", help="command to run (omit for interactive shell)"
    )
    parser.add_argument("--config", type=pathlib.Path, help="configuration file")

    args = parser.parse_args()

    try:
        if args.command:
            execute(args.command, load_config(args.config))
        else:
            shell(args.config)
    except (ValueError, OSError, KeyError) as e:
        print(f"error: {e}")
        sys.exit(1)
