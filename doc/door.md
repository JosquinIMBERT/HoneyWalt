# Door

## Description

The door is the server with a public IP to which the attacker will try to connect.
The ssh connections will be redirected through cowrie to the actually exposed device.
The outgoing connections of the devices will be redirected to the internet through this door (using wireguard tunnels)

For this purpose, we use AWS EC2 instances, but other kinds of servers could be used.
Here the important feature is only the public IP address.
HoneyWalt was tested with a freshly installed debian OS.