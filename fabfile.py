import json
import os
from fabric.api import *


@task
def load_config(filepath="configs/default_config.json"):
    try:
        with open(filepath) as f:
            conf = json.load(f)

        env.key_filename = []
        roles = {}
        for r in conf.keys():
            for k in conf[r]["key_filenames"]:
                env.key_filename.append(k)

            roles[r] = []
            for h in conf[r]["hosts"]:
                host = '{0}@{1}'.format(h["username"], h["url"])
                roles[r].append(host)

        env.roledefs.update(roles)

        print env.roledefs
        print env.key_filename
    except IOError as e:
        print('({0})'.format(e))


@task
@roles('server')
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
@roles('server')
def install_etcd(filepath):
    run('mkdir -p tmp')
    put(filepath, 'tmp')
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
@roles('server')
@runs_once
def install_server(go_file="lib/go.tar.gz", etcd_file="lib/etcd.tar.gz"):
    execute(install_go, go_file)
    execute(install_etcd, etcd_file)


@task
@roles('server')
def start_server():
    sudo('start etcd')


@task
@roles('server')
def stop_server():
    sudo('stop etcd')


@task
@roles('server')
def restart_server():
    sudo('restart etcd')


@task
@roles('client')
def install_client(filepath='lib/python-etcd-master.tar.gz'):
    run('mkdir -p tmp')
    put(filepath, 'tmp')
    filename = filepath.split('/')[-1]
    run('tar -xzf tmp/{0}'.format(filename))
    run('sudo apt-get install -y python-pip python-dev libffi-dev libssl-dev')
    run('''
        cd python-etcd-master
        sudo python setup.py install
        cd
        ''')
    put('lib/etcd-client.py')


@task
@roles('client')
def start_client(config_path, host, port=4001):
    run('python etcd-client.py {0} {1} {2} &'.format(config_path, host, port))
