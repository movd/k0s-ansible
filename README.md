![Supported k0s version](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/movd/k0s-ansible/main/supported-k0s-version.json) [![Ansible Lint status](https://github.com/movd/k0s-ansible/workflows/Ansible%20Lint/badge.svg?branch=main)](https://github.com/movd/k0s-ansible/actions) [![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/movd/k0s-ansible/latest)](https://github.com/movd/k0s-ansible/commits/main)

# k0s Ansible Playbook

Create a Kubernetes Cluster using Ansible and vanilla upstream Kubernetes distro [k0s](https://github.com/k0sproject/k0s)

This playbook is largely based on the extensive and outstanding work of the contributors of [k3s-ansible](https://github.com/k3s-io/k3s-ansible) and, of course, [kubespray](https://github.com/kubernetes-sigs/kubespray).

## Included Playbooks

`site.yml`:

```ShellSession
$ ansible-playbook site.yml -i inventory/multipass/inventory.yml
```

Your inventory must include at least one `initial_controller` and one `worker` node. To get a highly available control plane more `controller` nodes can be added. The first initial controller creates tokens that get written to the nodes when the playbook is executed.

`reset.yml`:

```ShellSession
$ ansible-playbook reset.yml -i inventory/multipass/inventory.yml
```

Deletes k0s all its files, directories and services from all hosts.

## Step by step guide

You can find a user guide on how to use this playbook in the [k0s documentation](https://docs.k0sproject.io/main/examples/ansible-playbook/).

## Example with multipass

For the quick creation of virtual machines, I have added a script that provisions a bunch of nodes via [multipass](https://github.com/canonical/multipass) and another small Python script that generates an Ansible inventory from the created instances.

Steps:

Create 5 instances with multipass and import your ssh public key with cloud-init (`create_instances.sh`):

```ShellSession
$ ./tools/multipass_create_instances.sh
Create cloud-init to import ssh key...
[1/5] Creating instance k0s-1 with multipass...
Launched: k0s-1
...
Name                    State             IPv4             Image
k0s-1                   Running           192.168.64.32    Ubuntu 20.04 LTS
k0s-2                   Running           192.168.64.33    Ubuntu 20.04 LTS
k0s-3                   Running           192.168.64.56    Ubuntu 20.04 LTS
k0s-4                   Running           192.168.64.57    Ubuntu 20.04 LTS
k0s-5                   Running           192.168.64.58    Ubuntu 20.04 LTS
```

Generate your Ansible inventory:

```ShellSession
$ cp -rfp inventory/sample inventory/multipass
$ ./tools/multipass_generate_inventory.py
Designate first instance as control plane
Created Ansible Inventory at: /Users/dev/k0s-ansible/tools/inventory.yml
$ cp tools/inventory.yml inventory/multipass/inventory.yml
```

Test the ssh connection to all instances in your `inventory.yml`:

```ShellSession
$ ansible -i inventory/multipass/inventory.yml -m ping all
k0s-4 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
k0s-1 | SUCCESS => {
...
```

Create your cluster:

```ShellSession
$ ansible-playbook site.yml -i inventory/multipass/inventory.yml
...
TASK [k0s/initial_controller : print kubeconfig command] *******************************************************
Friday 22 January 2021  15:32:44 +0100 (0:00:00.247)       0:04:25.177 ********
ok: [k0s-1] => {
    "msg": "To use Cluster: export KUBECONFIG=/Users/dev/k0s-ansible/inventory/multipass/artifacts/k0s-kubeconfig.yml"
}
...
PLAY RECAP *****************************************************************************************************
...
Friday 22 January 2021  15:32:58 +0100 (0:00:00.575)       0:04:39.234 ********
===============================================================================
download : Download k0s binary k0s-v0.10.0-beta1-amd64 ------------------------------------------------ 225.86s
prereq : Install apt packages -------------------------------------------------------------------------- 17.30s
k0s/initial_controller : Wait for k8s apiserver -------------------------------------------------------- 15.34s
k0s/controller : Wait for k8s apiserver ----------------------------------------------------------------- 3.36s
Gathering Facts ----------------------------------------------------------------------------------------- 1.35s
prereq : Create k0s Directories ------------------------------------------------------------------------- 0.86s
Gathering Facts ----------------------------------------------------------------------------------------- 0.84s
k0s/worker : Create k0s worker service with install command --------------------------------------------- 0.80s
Gathering Facts ----------------------------------------------------------------------------------------- 0.79s
k0s/initial_controller : Create k0s initial controller service with install command ------------------------- 0.76s
k0s/initial_controller : Enable and check k0s service --------------------------------------------------- 0.74s
k0s/controller : Create k0s controller service with install command ----------------------------------------- 0.72s
prereq : Write the k0s config file ---------------------------------------------------------------------- 0.69s
Gathering Facts ----------------------------------------------------------------------------------------- 0.68s
Gathering Facts ----------------------------------------------------------------------------------------- 0.65s
k0s/worker : Enable and check k0s service --------------------------------------------------------------- 0.58s
k0s/controller : Enable and check k0s service ----------------------------------------------------------- 0.53s
k0s/worker : Write the k0s token file on worker --------------------------------------------------------- 0.48s
k0s/controller : Write the k0s token file on controller ------------------------------------------------- 0.44s
k0s/initial_controller : Set controller IP in kubeconfig ------------------------------------------------ 0.32s
```

Connect to your new Kubernetes cluster. The config is ready to use in the `inventory/artifacts` directory:

```ShellSession
$ export KUBECONFIG=/Users/dev/k0s-ansible/inventory/multipass/artifacts/k0s-kubeconfig.yml
$ kubectl get nodes -o wide
NAME    STATUS   ROLES    AGE   VERSION        INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
k0s-4   Ready    <none>   17m   v1.20.2-k0s1   192.168.64.57   <none>        Ubuntu 20.04.1 LTS   5.4.0-62-generic   containerd://1.4.3
k0s-5   Ready    <none>   17m   v1.20.2-k0s1   192.168.64.58   <none>        Ubuntu 20.04.1 LTS   5.4.0-62-generic   containerd://1.4.3
$ kubectl run hello-k0s --image=quay.io/prometheus/busybox --rm -it --restart=Never --command -- sh -c "echo hello k0s"
hello k0s
pod "hello-k0s" deleted
```

### Want to throw away your cluster and start all over?

```ShellSession
$ multipass delete $(multipass list --format csv | grep 'k0s' | cut -d',' -f1)
$ multipass purge
```

## Test with Vagrant

It's assumed that vagrant is installed, if not, download and install it from their [website](https://www.vagrantup.com/downloads)

After that consult the [readme](Vagrant.md)

## How to Contribute

I welcome issues to and pull requests against this repository!
