#!/usr/bin/env python3
import subprocess
import json
import yaml
from pathlib import Path


def get_multipass_instances():
    try:
        # pipe multipass json list into dictionary
        result = subprocess.run(
            ['multipass', 'list', '--format', 'json'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        result_dict = json.loads(result)
        # filter for k0s instances
        filtered_list = list(
            filter(lambda k: 'k0s-' in k['name'], result_dict["list"]))
        return sorted(filtered_list, key=lambda x: x['name'])
    except Exception as e:
        print(e)


# Ansible inventory template
inventory = {'all':
             {'hosts': {},
              'vars': {'ansible_user': 'k0s'},
              'children': {'controller': {'hosts': []}, 'worker': {'hosts': []}}
              }
             }

instances = get_multipass_instances()


# Parse hosts for inventory
hosts = {}
for i in instances:
    hosts.update({i["name"]: {'ansible_host': i["ipv4"][0]}})

# Assign instances to their tasks.
# If more than 3 instances create two controllers
controllers = {}
workers = {}

# TODO:
# if len(instances) > 3:
#     print('add two controllers')
#     # first two become control planes
#     for i in instances[0:2]:
#         controllers.update({i["name"]: None})
#     # the rest become workers
#     for i in instances[2:]:
#         workers.update({i["name"]: None})
# else:

print('Designate first instance as control plane')
for i in instances[0:1]:
    controllers.update({i["name"]: None})
# The others become workers
for i in instances[1:]:
    workers.update({i["name"]: None})

# Fill inventory template with parsed values
inventory['all']['hosts'] = hosts
inventory['all']['children']['controller']['hosts'] = controllers
inventory['all']['children']['worker']['hosts'] = workers


def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')


# Set Representer that creates blanks instead of 'null' for empty objects
# https://stackoverflow.com/a/41786451
yaml.add_representer(type(None), represent_none)

# Write inventory as yaml
yaml_path = Path(__file__).with_name('inventory.yml')
f = open(yaml_path, 'w')
f.write(yaml.dump(inventory))
f.close

print(f'Created Ansible Inventory at: {yaml_path}')
