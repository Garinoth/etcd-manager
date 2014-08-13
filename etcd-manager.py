from fabric.api import execute, env
import fabfile
import actions
import argparse
import requests
import json

from urllib3.exceptions import TimeoutError

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--config_file",
    help="Configuration file to be used")
parser.add_argument(
    "action", type=str,
    choices=[
        'install_server', 'install_client', 'start_server', 'stop_server', 'restart_server',
        'get_discovery_token', 'start_client', 'stop_client', 'restart_client', 'read', 'write', 'delete'],
    help="Action to perform", nargs=1)
parser.add_argument(
    "arguments", type=str,
    help="Arguments for the selected action", nargs='*')

args = parser.parse_args()

action = args.action[0]
arguments = args.arguments
config_file = args.config_file

if config_file:
    execute(fabfile.load_config, config_file)
else:
    execute(fabfile.load_config)

if action == 'get_discovery_token':
    response = requests.get('https://discovery.etcd.io/new')
    if config_file:
        path = config_file
    else:
        path = "configs/default_config.json"
    try:
        with open(path) as f:
            conf = json.load(f)
        conf["server"]["discovery_token"] = response.text
        result = json.dumps(conf, indent=4, separators=(',', ': '))
        with open(path, 'w') as f:
            f.write(result)
    except IOError as e:
        print('ERROR: {0}'.format(e))
    print('Your new discovery token is: {0}'.format(response.text))

elif action in dir(fabfile):
    try:
        execute(getattr(fabfile, action), *arguments)
    except Exception, e:
        print('ERROR: {0}'.format(e))
        exit(1)

elif action in dir(actions):
    arguments.append(env.roledefs["server"][0])
    arguments.append(4001)
    try:
        res = getattr(actions, action)(*arguments)
        print '{0} succesful. Result:\n {1}'.format(action, res)
    except Exception, e:
        print('ERROR: {0}'.format(e))
        exit(1)

else:
    print 'Unrecognized action'
