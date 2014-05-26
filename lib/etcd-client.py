import etcd
import argparse
import os
import json

from urllib3.exceptions import TimeoutError


def _write_config(client, path):
    res = client.read('/', recursive=True)

    result = {}
    for o in res.leaves:
        result[o.key] = o.value

    result = json.dumps(result)
    try:
        with open(path, 'w') as f:
            f.write(result)
    except IOError as e:
        print('ERROR: {0}'.format(e))


parser = argparse.ArgumentParser()

parser.add_argument(
    "config_path",
    help="Path to the file where the configuration will be stored")
parser.add_argument(
    "host",
    help="Host to connect to at start")
parser.add_argument(
    "port", default=4001, nargs='?',
    help="Port where the etcd host will be listening")

args = parser.parse_args()

if not os.path.isdir(args.config_path):
    config_path = args.config_path
else:
    print('The config path "{0}" is not a file'.format(args.config_path))
    exit(1)

host = args.host
port = int(args.port)

client = etcd.Client(host=host, port=port)

_write_config(client, config_path)

while True:
    try:
        client.read('/', wait=True, recursive=True, timeout=5)
        _write_config(client, config_path)
    except TimeoutError as e:
        pass
