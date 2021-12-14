#!/usr/bin/env bash
if ! command -v multipass &> /dev/null
then
    echo "multipass could not be found"
    echo "Check <https://github.com/canonical/multipass> on how to install it"
    exit
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Default to 5 VMs
NUMBER_OF_VMS=${1:-5}

echo "Create cloud-init to import ssh key..."

# https://github.com/canonical/multipass/issues/965#issuecomment-591284180
cat <<EOF > "${DIR}"/multipass-cloud-init.yml
---
users:
  - name: k0s
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /usr/bin/bash
    ssh_authorized_keys:
      - $( cat "$(ls -1 ~/.ssh/id_*.pub | head -1)" )
EOF

for ((i = 1 ; i <= "${NUMBER_OF_VMS}" ; i++)); do
  echo "[${i}/${NUMBER_OF_VMS}] Creating instance k0s-${i} with multipass..."
  multipass launch \
  --name k0s-"${i}" \
  --cloud-init "${DIR}"/multipass-cloud-init.yml \
  --cpus 2 \
  --mem 2048M \
  --disk 20G
done

multipass list 



