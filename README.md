# or_scripts

Scripts to run optimization benchmarks on a cluster of mini-PCs and collect the
results into a table. Instances are JSON files; each algorithm stores its
results in the instance file under its own key.

All scripts read `config.toml` (or the file given with `--config`).

## Setup

```
pip install -r requirements.txt
```

`install_gurobi.sh` installs Gurobi 10.0.1 in `/opt/gurobi` (run as root).

## Scripts

| Script | Purpose |
|---|---|
| `benchmarks.py INPUT_DIR` | Runs each `./bin/<exec>` listed in `[benchmarks].execs` on every `*.json` in `INPUT_DIR`. The other `[benchmarks]` keys are passed as `--key value`. Launch it from the project root. |
| `cluster.py [COMMAND]` | Controls the remote machines `minipc<N>` (`[cluster].indices`) over ssh/scp. No command starts an interactive shell. |
| `collect.py INPUT_DIR [--format csv\|excel]` | Builds a table from the result JSONs into `doc/<INPUT_DIR>.csv` or `.xlsx`, as set in `[collect]`. |
| `merge.py DIR1 DIR2 ...` | Merges the JSONs of the other directories into the same-named files of `DIR1`, in place. |
| `clean.py INPUT_DIR --exec ALGO ...` | Removes the results of the given algorithms from every JSON in `INPUT_DIR`. |
| `install_gurobi.sh` | Downloads and installs Gurobi. |

## cluster.py commands

- `deploy`: copy `bin`, `benchmarks.py` and `config.toml` to each machine
- `config`: copy only `config.toml`
- `data`: distribute the local instances round-robin over the machines
- `run`: start `benchmarks.py data` in the background on each machine
- `stop`: kill `benchmarks.py` and the running binaries
- `ps`: show the top CPU process of each machine
- `ls`: list the remote directory
- `collect`: download the remote results into `data/<data_dir>`
- `clean`: wipe the remote directory
- `clean_data`: wipe only the remote `data` directory
- `all`: `clean`, `deploy`, `data`, `run`
- `edit_config`: open the config in `$EDITOR`

In the interactive shell there are also `reload`, `help` and `quit`.

## Typical workflow

```
./cluster.py all        # deploy and start the benchmarks
./cluster.py ps         # check progress
./cluster.py collect    # download the results
./merge.py a/ b/        # (optional) combine results of different runs
./collect.py data/x     # build the table in doc/
```

Use `./clean.py DIR --exec ALGO` to reset the results before re-running.

## Configuration

`config.toml` has three sections: `[collect]` (table layout), `[cluster]`
(machines and directories) and `[benchmarks]` (binaries and their options).
