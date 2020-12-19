# k0s Ansible Playbook

Create a Kubernetes Cluster using Ansible and k0s (and multipass).

This script is largely based on the extensive and outstanding work of the contributors of [k3s-ansible](https://github.com/k3s-io/k3s-ansible) and, of course, [kubespray](https://github.com/kubernetes-sigs/kubespray). I put it together to learn about Ansible and the new single binary and vanilla upstream Kubernetes distro [k0s](https://github.com/k0sproject/k0s).

For the quick creation of virtual machines, I have added a script that provisions a bunch of nodes via [multipass](https://github.com/canonical/multipass) and another small Python script that generates an Ansible inventory from the created instances.

## Example with multipass

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
Created Ansible Inventory at: /Users/moritz/dev/k0s-ansible/tools/inventory.yml
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
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
k0s-3 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
k0s-2 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
k0s-5 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
```

Create your cluster:

```ShellSession
$ ansible-playbook site.yml -i inventory/multipass/inventory.yml
...
TASK [k0s/controller : print kubeconfig command] ****************************************************************************************************************
Friday 18 December 2020  18:05:36 +0100 (0:00:00.256)       0:01:57.277 *******
ok: [k0s-1] => {
    "msg": "To use Cluster: export KUBECONFIG=/Users/moritz/dev/k0s-ansible/inventory/multipass/artifacts/k0s-kubeconfig.yml"
}
...
PLAY RECAP ******************************************************************************************************************************************************
k0s-1                      : ok=18   changed=12   unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-2                      : ok=9    changed=6    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-3                      : ok=9    changed=6    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-4                      : ok=9    changed=6    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
k0s-5                      : ok=9    changed=6    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0

Friday 18 December 2020  18:05:39 +0100 (0:00:00.990)       0:02:00.104 *******
===============================================================================
download : Download k0s binary amd64 -------------------------------------------------------------------------------------------------------------------- 99.68s
k0s/controller : Wait for k8s apiserver ------------------------------------------------------------------------------------------------------------------ 7.38s
k0s/controller : Create join worker token ---------------------------------------------------------------------------------------------------------------- 3.35s
Gathering Facts ------------------------------------------------------------------------------------------------------------------------------------------ 2.18s
Gathering Facts ------------------------------------------------------------------------------------------------------------------------------------------ 1.06s
k0s/worker : Enable and check k0s service ---------------------------------------------------------------------------------------------------------------- 0.99s
k0s/controller : Enable and check k0s service ------------------------------------------------------------------------------------------------------------ 0.93s
Gathering Facts ------------------------------------------------------------------------------------------------------------------------------------------ 0.68s
k0s/controller : Write the k0s config file --------------------------------------------------------------------------------------------------------------- 0.61s
k0s/worker : Copy k0s service file ----------------------------------------------------------------------------------------------------------------------- 0.47s
prereq : Create a Directory "/etc/k0s" ------------------------------------------------------------------------------------------------------------------- 0.41s
k0s/controller : Copy k0s service file ------------------------------------------------------------------------------------------------------------------- 0.38s
k0s/controller : Set controller IP in kubeconfig --------------------------------------------------------------------------------------------------------- 0.34s
prereq : Create a Directory "/usr/libexec/k0s/" ---------------------------------------------------------------------------------------------------------- 0.30s
prereq : Create a Directory "/var/lib/k0s" --------------------------------------------------------------------------------------------------------------- 0.29s
k0s/worker : Create a Directory "/var/lib/k0s" ----------------------------------------------------------------------------------------------------------- 0.27s
k0s/controller : Copy kubectl binary to ansible host ----------------------------------------------------------------------------------------------------- 0.26s
k0s/controller : Copy config file to user home directory ------------------------------------------------------------------------------------------------- 0.22s
download : Download k0s binary arm64 --------------------------------------------------------------------------------------------------------------------- 0.11s
k0s/controller : print token ----------------------------------------------------------------------------------------------------------------------------- 0.03s
```

Connect to your new Kubernetes cluster. The config is ready to use in the `inventory/artifacts` directory:

```ShellSession
$ export KUBECONFIG=/Users/moritz/k0s-ansible/inventory/multipass/artifacts/k0s-kubeconfig.yml
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

## Todo

- Support multiple control plane nodes
