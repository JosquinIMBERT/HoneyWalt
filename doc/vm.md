# Virtual Machine

## Description

The virtual machine (VM) hosts the Walt server that manages the devices.
It is considered to be in the demilitarized zone (DMZ).

## Phases

The VM can be started in two different phases:

1) The phase 1 is the commit phase. The VM is booted without the snapshot modes. Consequently, the modifications to the file system are persistent. During this phase, we don't expose the honeypot to the attackers (all tunnels are off).

2) The phase 2 is the production phase. The VM is booted with the snapshot mode which means that the modifications are volatile. This phase corresponds to when the honeypot is running. Consequently, the VM is esposed and unsafe (an attacker could enter from the WalT network).