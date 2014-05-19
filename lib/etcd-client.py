import etcd
import argparse

from urllib3.exceptions import TimeoutError


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

config_path = args.config_path
host = args.host
port = int(args.port)

client = etcd.Client(host=host, port=port)

_write_config(client, config_path)

while True:
    try:
        client.read('/', wait=True, recursive=True, timeout=None)
        _write_config(client, config_path)
    except TimeoutError as e:
        pass


def _write_config(client, path):
    res = client.read('/', recursive=True)
    try:
        with open(path, 'w') as f:
            f.write(res)
    except IOError as e:
        print('({0})'.format(e))