import etcd


def connect(host, port):
    return etcd.Client(host=host, port=port)


def write(key, value, host, port):
    client = connect(host, port)
    return client.write(key, value)


def read(key, host, port):
    client = connect(host, port)
    return client.read(key)


def delete(key, host, port):
    client = connect(host, port)
    return client.delete(key)
