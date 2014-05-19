from fabric.api import execute, env
import fabfile
import actions
import argparse


parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--config_file",
    help="Configuration file to be used")
parser.add_argument(
    "action", type=str,
    choices=['install_server', 'install_client', 'start',
             'stop', 'restart', 'read', 'write', 'delete'],
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
    execute(getattr(fabfile, action), *arguments)

elif action in dir(actions):
    arguments.append(env.hosts[0])
    arguments.append(4001)
    res = getattr(actions, action)(*arguments)
    print res
