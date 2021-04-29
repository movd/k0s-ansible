$script = <<SCRIPT
sudo apt-get update
sudo apt-get install -y curl
echo "IP Addresses:" >>/etc/issue
for iface in $(ip -br link | awk '!/lo/ { print $1}'); do
  echo "$iface - \\4{$iface}" >>/etc/issue
done
SCRIPT

# How many VMs to create
VMS = 5

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.provision "shell", inline: $script

  # Use the same key for each machine
  # ssh-add ~/.vagrant/insecure_private_key
  config.ssh.insert_key = false

  config.vbguest.auto_update = false

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 1024
    vb.cpus = 2
    vb.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
    vb.customize ["modifyvm", :id, "--audio", "none"]
  end

  (1..VMS).each do |i|
    config.vm.define "k0s-#{i}" do |box|
      box.vm.hostname = "k0s-#{i}"
      box.vm.network "private_network", ip: "192.168.56.15#{i}"
    end
  end

end
