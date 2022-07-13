# Door

## Description

The door is the server with a public IP to which the attacker will try to connect.
The ssh connections will be redirected through cowrie to the actually exposed device.
The outgoing connections of the devices will be redirected to the internet through this door (using wireguard tunnels).

For this purpose, we use AWS EC2 instances, but other kinds of servers could be used.
Here the important feature is only the public IP address.
HoneyWalt was tested with a freshly installed debian OS on the EC2 instances.

## Configuration

The doors configurations can be edited using the ```python3 honeywalt.py door <subcmd>``` command.
Thus, we can add a door, change it's configuration and remove it with the ```add```, ```change``` and ```del``` subcommands.

Two parameters are used to configure a door:

- The public IP of the door,
- The backend device that will actually host the connection.

The public key used by HoneyWalt will have to be manually added to the root's authorized_keys file to give HoneyWalt an ssh access to the door. This key is given when the door is added to the configuration.

## Technical details

When a door is added to HoneyWalt, the ssh daemon of that door will be moved to another port to free the port 22 (connections on this port will be redirected to the devices).

A Wireguard server will also be added to redirect the backend device's traffic through the corresponding door.