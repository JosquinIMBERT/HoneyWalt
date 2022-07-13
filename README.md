# HoneyWalt

## Description

HoneyWalt is a scalable, manageable, reproducible and realistic honeypot.
It is based on real devices that can be plugged directly to the honeypot.

HoneyWalt was built with Walt: a plateform for network experiments that allows us to quickly erase the attackers modifications from the devices.

The architecture of HoneyWalt is mainly based on four elements:

- Doors: the entry points of the honeypot. The doors are servers with public IPs. They redirect their port 22 (ssh) to the controller's cowrie processes. Run ```python3 honeywalt.py door help``` for more information.
- Controller: the central point of the honeypot. It is in charge of controlling the attacker's traffic, accepting and redirecting the connections and gathering some logs. Run ```python3 honeywalt.py controller help``` for more information.
- Virtual Machine (VM): the entry point of the demilitarized zone (the zone that can be attacked). It runs the Walt server, it redirects the connections from cowrie (on the controller) to the devices and it redirects the outgoing connections to the door with wireguard tunnels.
- Devices: the machines that are actually exposed. They have a weak security (default usernames and passwords, ssh with password allowed for root) and are all connected to the same LAN. Run ```python3 honeywalt.py device help``` for more information.

When using HoneyWalt, you also need to know about the OS images - called Walt images - deployed by the Walt server on the devices. You can choose which image you want to deploy on each device. Run ```python3 honeywalt.py image help``` for more information.

## References

- Cowrie: https://github.com/cowrie/cowrie
- Walt: https://github.com/drakkar-lig/walt-python-packages
- Wireguard: https://www.wireguard.com/