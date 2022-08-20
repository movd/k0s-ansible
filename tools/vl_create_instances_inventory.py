#!/usr/bin/env python3

import argparse
import getpass
import yaml

from pathlib import Path
from yaml import SafeDumper

try:
    import virt_lightning
except ImportError:
    print(
        """
        Can't import virt-lightning. Install it as described at 
        
        https://github.com/virt-lightning/virt-lightning
        
        or use scripts for Multipass
        """
    )

import virt_lightning.api as vla
from virt_lightning.configuration import Configuration


def numbers_of_vm_val(n):
    result = int(n)
    if result < 1:
        raise ValueError
    return result


DISTRO = "ubuntu-18.04"
VM_CONFIG = {"distro": DISTRO, "memory": 2048, "vcpus": 2}
USER = getpass.getuser()
INVENTORY_TEMPLATE = {
    "all": {
        "hosts": {},
        "vars": {"ansible_user": USER},
        "children": {
            "initial_controller": {"hosts": {}},
            "controller": {"hosts": {}},
            "worker": {"hosts": {}},
        },
    }
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tool to prepare VMs and Ansible inventory"
    )
    parser.add_argument(
        "number_of_vms",
        type=numbers_of_vm_val,
        default="5",
        nargs="?",
        help="Number of VMs to deploy",
    )

    args = parser.parse_args()

    configuration = Configuration()
    configuration.username = USER

    if DISTRO not in vla.distro_list(configuration=configuration):
        print(f"Distro {DISTRO} not found, fetching...")
        vla.fetch(configuration=configuration, distro=DISTRO)

    if args.number_of_vms < 4:
        vm_name_postfix = ["initial_controller"] + ["worker"] * (
            args.number_of_vms - 1
        )
    else:
        vm_name_postfix = (
            ["initial_controller"]
            + ["controller"] * 2
            + ["worker"] * (args.number_of_vms - 3)
        )
    vm_names = [
        f"k0s-{idx}-{postfix}" for idx, postfix in enumerate(vm_name_postfix)
    ]

    # Check if we have some VMs running. Just to form message to user, VL skips
    # creating of VM if it exists
    running_vms = [x["name"] for x in vla.status(configuration=configuration)]
    for vm_name in vm_names:
        if vm_name in running_vms:
            print(f"{vm_name} is running")
            continue
        print(f"Spinning up {vm_name}")
        vla.start(configuration=configuration, name=vm_name, **VM_CONFIG)

    # VL outputs inventory as text, so some parsing is needed
    inventory = {
        x.split(" ")[0]: x.split(" ")[1].split("=")[1]
        for x in vla.ansible_inventory(configuration=configuration).split("\n")
        if x != "" and x.split(" ")[0] in vm_names
    }

    INVENTORY_TEMPLATE["all"]["hosts"] = {
        k: {"ansible_host": v} for k, v in inventory.items()
    }
    INVENTORY_TEMPLATE["all"]["children"]["initial_controller"]["hosts"] = {
        x: None for x in inventory if "initial_controller" in x
    }
    INVENTORY_TEMPLATE["all"]["children"]["controller"]["hosts"] = {
        x: None for x in inventory if "-controller" in x
    }
    INVENTORY_TEMPLATE["all"]["children"]["worker"]["hosts"] = {
        x: None for x in inventory if "worker" in x
    }

    # Dump blanks instead of 'null' by using SafeDumper
    # https://stackoverflow.com/a/37445121
    SafeDumper.add_representer(
        type(None),
        lambda dumper, value: dumper.represent_scalar(
            "tag:yaml.org,2002:null", ""
        ),
    )

    # Write inventory as yaml
    yaml_path = Path(__file__).with_name("inventory.yml")
    with open(yaml_path, "w") as f:
        f.write(
            yaml.safe_dump(
                INVENTORY_TEMPLATE,
                default_flow_style=False,
                explicit_start=True,
            )
        )

    print(f"Created Ansible Inventory at: {yaml_path}")
