#! /usr/bin/env python3

import pathlib
import argparse
import subprocess
import requests
import socket
import datetime
import tomllib
import time
import sys
import os

def send_message_to_telegram(msg):
    token = "6276168703:AAHuAEsAKTu08oEHbEPBF2PUHm4_IhQ7z2c"
    chat_id = "60446563"

    if not token or not chat_id:
        return

    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}'
    try:
        requests.get(url)
    except ConnectionError:
        print('no connection')


# must be launch from project root dir
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=pathlib.Path, help='instances directory')
    parser.add_argument('--config', type=pathlib.Path, help='configuration file')

    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print('input_dir does not exist')
        sys.exit()

    if not args.input_dir.glob('**/*.json'):
        print('input_dir does not contains any instance')
        sys.exit()

    if args.config:
        config_path = args.config
    elif pathlib.Path('config.toml').exists():
        config_path = pathlib.Path('config.toml')
    else:
        print('no configuration available')
        sys.exit()

    with open(config_path, 'rb') as f:
        config = tomllib.load(f)['benchmarks']

    execs = config['execs']

    cmdl_args = []
    for k, v in config.items():
        if k != 'execs':
            cmdl_args.append(f'--{k}')
            cmdl_args.append(str(v))

    for cmd in execs:
        cmd = './bin/' + cmd
        start = time.time();
        for input in args.input_dir.glob('**/*.json'):
            print(f'launching {cmd} with input {input}...')
            subprocess.run([cmd, input] + cmdl_args)

        end = time.time();
        elapsed_time = datetime.timedelta(seconds=(end - start))

        hostname = os.environ.get('HOSTNAME', socket.gethostname())
        msg = f'run of {cmd} on {hostname} completed in {elapsed_time}'
        send_message_to_telegram(msg)
