#!/usr/bin/env python3
import subprocess
import json
import yaml
from yaml import SafeDumper
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
              'children': {
                  'initial_controller': {'hosts': []},
                  'controller': {'hosts': []},
                  'worker': {'hosts': []}
             }
             }
             }

instances = get_multipass_instances()


# Parse hosts for inventory
hosts = {}
for i in instances:
    hosts.update({i["name"]: {'ansible_host': i["ipv4"][0]}})

# Assign instances to their tasks.
# If more than four instances create three controllers
initial_controller = {}
controllers = {}
workers = {}

if len(instances) > 4:
    for i in instances[0:1]:
        initial_controller.update({i["name"]: None})
    for i in instances[1:3]:
        controllers.update({i["name"]: None})
    for i in instances[3:]:
        workers.update({i["name"]: None})
    print('Designated first three instances as control plane nodes.')
else:
    for i in instances[0:1]:
        initial_controller.update({i["name"]: None})
    # The others become workers
    for i in instances[1:]:
        workers.update({i["name"]: None})
    print('Designated first instance as control plane node.')

# Fill inventory template with parsed values
inventory['all']['hosts'] = hosts
inventory['all']['children']['initial_controller']['hosts'] = initial_controller
inventory['all']['children']['controller']['hosts'] = controllers
inventory['all']['children']['worker']['hosts'] = workers

# Dump blanks instead of 'null' by using SafeDumper
# https://stackoverflow.com/a/37445121
SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(
        u'tag:yaml.org,2002:null', '')
)

# Write inventory as yaml
yaml_path = Path(__file__).with_name('inventory.yml')
f = open(yaml_path, 'w')
f.write(yaml.safe_dump(inventory, default_flow_style=False, explicit_start=True))
f.close

print(f'Created Ansible Inventory at: {yaml_path}')
