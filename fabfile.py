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
        env.client = conf["client"]

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
        print('ERROR: {0}'.format(e))

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
    pwd = run('pwd')
    upstart_script = '''
description "etcd client"

start on startup
stop on shutdown

respawn
respawn limit 15 5

script
    python {0}/etcd-client.py {1} {2} 4001 >> /var/log/etcd-client.log 2>&1
end script

post-start script
end script
'''.format(pwd, '{0}/{1}'.format(pwd, env.client["config_path"]), env.roledefs["server"][0])
    try:
        f = open('etcd-client.conf', 'w')
        try:
            f.write(upstart_script)
        finally:
            f.close()
            try:
                os.remove(filename)
            except OSError:
                pass
    except IOError as e:
        print('ERROR: {0}'.format(e))

    put('etcd-client.conf', 'tmp')
    sudo('mv tmp/etcd-client.conf /etc/init/etcd-client.conf')


@task
@roles('client')
def start_client():
    sudo('start etcd-client')


@task
@roles('client')
def stop_client():
    sudo('stop etcd-client')


@task
@roles('client')
def restart_client():
    sudo('restart etcd-client')
