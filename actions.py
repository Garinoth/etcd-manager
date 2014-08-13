import etcd
from urllib3.exceptions import TimeoutError


def connect(host, port):
    return etcd.Client(host=host, port=port, allow_reconnect=True)


def write(key, value, host, port):
    client = connect(host, port)
    try:
        return client.write(key, value)
    except TimeoutError as e:
        print('ERROR: {0}'.format(e))


def read(key, host, port):
    client = connect(host, port)
    try:
        return client.read(key)
    except TimeoutError as e:
        print('ERROR: {0}'.format(e))


def delete(key, host, port):
    client = connect(host, port)
    try:
        return client.delete(key)
    except TimeoutError as e:
        print('ERROR: {0}'.format(e))
