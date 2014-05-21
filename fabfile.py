import json
import os
from fabric.api import *


@task
def load_config(filepath="configs/default_config.json", kind="server"):
    try:
        with open(filepath) as f:
            conf = json.load(f)

        env.user = conf[kind]["default_username"]
        env.key_filename = conf[kind]["key_filenames"]

        env.hosts = []
        for h in conf[kind]["hosts"]:
            if h["username"] != "":
                host = '{0}@{1}'.format(h["username"], h["url"])
            else:
                host = '{0}'.format(h["url"])
            env.hosts.append(host)

    except IOError as e:
        print('({0})'.format(e))


@task
def install_go(filepath):
    run('mkdir -p tmp')
    put(filepath, 'tmp')
    filename = filepath.split('/')[-1]
    run('tar -xzf tmp/{0}'.format(filename))
    run('''
        echo >> $HOME/.profile
        echo "### GO variables" >> $HOME/.profile
        echo \'export GOROOT=$HOME/go\' >> $HOME/.profile
        echo \'export PATH=$PATH:$GOROOT/bin\' >> $HOME/.profile
        ''')


@task
def install_etcd(filepath):
    run('mkdir -p tmp')
    #put(filepath, 'tmp')
    filename = filepath.split('/')[-1]
    run('tar -xzf tmp/{0}'.format(filename))
    run('''
        cd etcd
        ./build
        cd
        ''')
    pwd = run('pwd')
    upstart_script = '''
description "etcd server"

start on startup
stop on shutdown

respawn
respawn limit 15 5

script
    exec {0}/etcd/bin/etcd >> /var/log/etcd.log 2>&1
end script

post-start script
end script
'''.format(pwd)
    try:
        f = open('etcd.conf', 'w')
        try:
            f.write(upstart_script)
        finally:
            f.close()
            try:
                os.remove(filename)
            except OSError:
                pass
    except IOError as e:
        print('({0})'.format(e))

    put('etcd.conf', 'tmp')
    sudo('mv tmp/etcd.conf /etc/init/etcd.conf')


@task
def start():
    sudo('start etcd')


@task
def stop():
    sudo('stop etcd')


@task
def restart():
    sudo('restart etcd')


@task
@runs_once
def install_server(go_file="lib/go.tar.gz", etcd_file="lib/etcd.tar.gz"):
    execute(install_go, go_file)
    execute(install_etcd, etcd_file)


@task
def install_client():
    pass
