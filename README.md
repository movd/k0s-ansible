# k0s Ansible Playbook

Create a Kubernetes Cluster using Ansible and k0s.

This playbook is largely based on the extensive and outstanding work of the contributors of [k3s-ansible](https://github.com/k3s-io/k3s-ansible) and, of course, [kubespray](https://github.com/kubernetes-sigs/kubespray). I put it together to learn about Ansible and the new single binary and vanilla upstream Kubernetes distro [k0s](https://github.com/k0sproject/k0s).

## Included Playbooks

`site.yml`:

```ShellSession
$ ansible-playbook site.yml -i inventory/multipass/inventory.yml
```

Install k0s on `worker` and `controller` host in your inventory. Currently creates one Kubernetes control plane server.

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
[2/5] Creating instance k0s-2 with multipass...
Launched: k0s-2
[3/5] Creating instance k0s-3 with multipass...
Launched: k0s-3
[4/5] Creating instance k0s-4 with multipass...
Launched: k0s-4
[5/5] Creating instance k0s-5 with multipass...
Launched: k0s-5
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
Tuesday 22 December 2020  17:43:20 +0100 (0:00:00.257)       0:00:41.287 ******
ok: [k0s-1] => {
    "msg": "To use Cluster: export KUBECONFIG=/Users/dev/k0s-ansible/inventory/multipass/artifacts/k0s-kubeconfig.yml"
}
...
PLAY RECAP *****************************************************************************************************
k0s-1                      : ok=21   changed=11   unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-2                      : ok=10   changed=5    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-3                      : ok=10   changed=5    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-4                      : ok=9    changed=5    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-5                      : ok=9    changed=5    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-6                      : ok=9    changed=5    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-7                      : ok=9    changed=5    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0

Tuesday 22 December 2020  17:43:36 +0100 (0:00:01.204)       0:00:57.478 ******
===============================================================================
prereq : Install apt packages -------------------------------------------------------------------------- 22.70s
k0s/controller : Wait for k8s apiserver ----------------------------------------------------------------- 4.30s
k0s/initial_controller : Create worker join token ------------------------------------------------------- 3.38s
k0s/initial_controller : Wait for k8s apiserver --------------------------------------------------------- 3.36s
download : Download k0s binary k0s-v0.9.0-rc1-amd64 ----------------------------------------------------- 3.11s
Gathering Facts ----------------------------------------------------------------------------------------- 2.85s
Gathering Facts ----------------------------------------------------------------------------------------- 1.95s
prereq : Create k0s Directories ------------------------------------------------------------------------- 1.53s
k0s/worker : Enable and check k0s service --------------------------------------------------------------- 1.20s
prereq : Write the k0s config file ---------------------------------------------------------------------- 1.09s
k0s/initial_controller : Enable and check k0s service --------------------------------------------------- 0.94s
k0s/controller : Enable and check k0s service ----------------------------------------------------------- 0.73s
Gathering Facts ----------------------------------------------------------------------------------------- 0.71s
Gathering Facts ----------------------------------------------------------------------------------------- 0.66s
Gathering Facts ----------------------------------------------------------------------------------------- 0.64s
k0s/worker : Write the k0s token file on worker --------------------------------------------------------- 0.64s
k0s/worker : Copy k0s service file ---------------------------------------------------------------------- 0.53s
k0s/controller : Write the k0s token file on controller ------------------------------------------------- 0.41s
k0s/controller : Copy k0s service file ------------------------------------------------------------------ 0.40s
k0s/initial_controller : Copy k0s service file ---------------------------------------------------------- 0.36s
```

Connect to your new Kubernetes cluster. The config is ready to use in the `inventory/artifacts` directory:

```ShellSession
$ export KUBECONFIG=/Users/dev/k0s-ansible/inventory/multipass/artifacts/k0s-kubeconfig.yml
$ kubectl get nodes -o wide
NAME    STATUS   ROLES    AGE     VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
k0s-2   Ready    <none>   2m42s   v1.19.4   192.168.64.33   <none>        Ubuntu 20.04.1 LTS   5.4.0-54-generic   containerd://1.4.3
k0s-3   Ready    <none>   2m42s   v1.19.4   192.168.64.56   <none>        Ubuntu 20.04.1 LTS   5.4.0-54-generic   containerd://1.4.3
k0s-4   Ready    <none>   2m42s   v1.19.4   192.168.64.57   <none>        Ubuntu 20.04.1 LTS   5.4.0-54-generic   containerd://1.4.3
k0s-5   Ready    <none>   2m42s   v1.19.4   192.168.64.58   <none>        Ubuntu 20.04.1 LTS   5.4.0-54-generic   containerd://1.4.3
$ kubectl run hello-k0s --image=quay.io/prometheus/busybox --rm -it --restart=Never --command -- sh -c "echo hello k0s"
hello k0s
pod "hello-k0s" deleted
```

### Want to trow away your cluster and start all over?

```ShellSession
$ multipass delete $(multipass list --format csv | grep 'k0s' | cut -d',' -f1)
$ multipass purge
```
