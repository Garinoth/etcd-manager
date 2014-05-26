from fabric.api import execute, env
import fabfile
import actions
import argparse

from urllib3.exceptions import TimeoutError

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--config_file",
    help="Configuration file to be used")
parser.add_argument(
    "action", type=str,
    choices=['install_server', 'install_client', 'start_server', 'stop_server',
             'restart_server', 'start_client', 'read', 'write', 'delete'],
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

if action in dir(fabfile):
    try:
        execute(getattr(fabfile, action), *arguments)
    except Exception, e:
        print('ERROR: {0}'.format(e))

elif action in dir(actions):
    arguments.append(env.roledefs["server"][0])
    arguments.append(4001)
    try:
        res = getattr(actions, action)(*arguments)
        print '{0} succesful. Result:\n {1}'.format(action, res)
    except Exception, e:
        print('ERROR: {0}'.format(e))

else:
    print 'Unrecognized action'
