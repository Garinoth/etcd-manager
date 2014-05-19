import etcd
import json
import argparse

from urllib3.exceptions import TimeoutError


def first_read(client):
    res = client.read('/', recursive=True)
    print res

parser = argparse.ArgumentParser()

parser.add_argument(
    "host",
    help="Host to connect to at start")
parser.add_argument(
    "port", default=4001, nargs='?',
    help="Port where the etcd host will be listening")

args = parser.parse_args()

host = args.host
port =int(args.port)

client = etcd.Client(host=host, port=port)

first_read(client)

while False:
    try:
        res = client.read('/', wait=True, recursive=True, timeout=None)
        print res.key
    except TimeoutError as e:
        pass