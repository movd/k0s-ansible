## Included Playbooks

`site.yml`:

```ShellSession
$ ansible-playbook site.yml -i inventory/vagrant/inventory.yml
```

Your inventory must include at least one `initial_controller` and one `worker` node. To get a highly available control plane more `controller` nodes can be added. The first initial controller creates tokens that get written to the nodes when the playbook is executed.

Since vagrant adds a NAT interface to your VMs by default, we have to use a custom k0s.config so that the right network interface is used for k0s, for that we have defined `k0s_use_custom_config: true` in [group_vars/all.yml](inventory/vagrant/group_vars/all.yml)

`reset.yml`:

```ShellSession
$ ansible-playbook reset.yml -i inventory/vagrant/inventory.yml
```

Deletes k0s all its files, directories and services from all hosts.

## Example with Vagrant

For the quick creation of virtual machines, there's a [Vagrantfile](Vagrantfile) included  
By default it creates 5 VMs, to override this , edit the file and define your desired number of VMs at the top of the file (look for `VMS`)

Steps:

- Examine the `Vagrantfile` and make sure the network prefix assigned to the **private_network** is what you expect.

- Make sure you have the plugin `vagrant-vbguest` installed: `vagrant plugin install vagrant-vbguest`

- Create instances with vagrant

```ShellSession
$ vagrant up
```

- Edit the [inventory](inventory/vagrant/inventory.yml) file and check if the information is correct

- Test the ssh connection to all instances in your `inventory.yml`:

```ShellSession
$ ansible -i inventory/vagrant/inventory.yml -m ping all
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
$ ansible-playbook site.yml -i inventory/vagrant/inventory.yml
...
TASK [k0s/initial_controller : print kubeconfig command] *******************************************************
Friday 22 January 2021  15:32:44 +0100 (0:00:00.247)       0:04:25.177 ********
ok: [k0s-1] => {
    "msg": "To use Cluster: export KUBECONFIG=/Users/dev/k0s-ansible/inventory/vagrant/artifacts/k0s-kubeconfig.yml"
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
$ export KUBECONFIG=/Users/dev/k0s-ansible/inventory/vagrant/artifacts/k0s-kubeconfig.yml
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
$ vagrant destroy -f
```
