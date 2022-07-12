import subprocess
from string import Template

import glob
from utils import eprint, run


# Generate the (public and private) keys of the wireguard servers and clients
# May be it could be simplified (we may not neet to generate the keys on the
# host that will use it)
def gen_keys():
	conf = glob.CONFIG

	# Key generation template
	keygen_cmd = "umask 077; \
		wg genkey >privkey; \
		wg pubkey <privkey >pubkey; \
		cat privkey; \
		cat pubkey"
	ssh_temp = Template("ssh root@${ip} -i {keypath} -p {port} \"${command}\"")

	# Servers keys
	serv_privkeys = []
	serv_pubkeys = []
	ssh_door_key = to_root_path("var/key/id_door")
	for door in conf["door"]:
		command = ssh_temp.substitute({
			"ip":door["host"],
			"keypath":ssh_door_key,
			"port":door["realssh"],
			"command":keygen_cmd
		})
		error_msg = "wireguard.gen_keys: error: ssh command returned non-zero code"
		res = run(command, error_msg, output=True)
		privkey, pubkey = res.split("\n", 1)
		serv_privkeys += [ privkey ]
		serv_pubkeys += [ pubkey ]

	# Clients keys
	cli_privkeys = []
	cli_pubkeys = []
	ssh_vm_key = to_root_path("var/key/id_olim")
	for dev in conf["device"]:
		command = ssh_temp.substitute({
			"ip": "10.0.0.2",
			"keypath": ssh_vm_key,
			"port": 22,
			"command": keygen_cmd
		})
		error_msg = "wireguard.gen_keys: error: ssh command returned non-zero code"
		res = run(command, error_msg, output=True)
		privkey, pubkey = res.split("\n", 1)
		cli_privkeys += [ privkey ]
		cli_pubkeys += [ pubkey ]

	return serv_privkeys, serv_pubkeys, cli_privkeys, cli_pubkeys


def gen_configurations(serv_privkeys, serv_pubkeys, cli_privkeys, cli_pubkeys):
	conf = glob.CONFIG

	# General variables
	conf_path = to_root_path("run/wireguard/")
	scp_temp = Template("scp "+conf_path+"${file} \
		root@${addr}:${remote_path} \
		-i ${key} -p ${port}")

	# Server Configuration Templates
	with open(to_root_path("var/template/wg_server_itf.txt"), "r") as temp_file:
		server_itf_temp = Template(temp_file.read())
	with open(to_root_path("var/template/wg_server_peer.txt"), "r") as temp_file:
		server_peer_temp = Template(temp_file.read())

	i=0
	for door in conf["door"]:
		# Generate Configuration
		conf_filename = "server"+str(i)
		server_config = server_itf_temp.substitute({
			"server_privkey": serv_privkeys[i]
		})
		for cli_pubkey in cli_pubkeys:
			server_config += server_peer_temp.substitute({
				"vm_pubkey": cli_pubkey
			})
		# Write configuration to a file
		with open(os.path.join(conf_path, conf_filename), "w") as conf_file:
			conf_file.write(server_config)
		# Copy configuration to the server
		scp_cmd = scp_temp.substitute({
			"file":conf_filename,
			"addr":door["host"],
			"remote_path":"/etc/wireguard/wg.conf",
			"key":to_root_path("var/key/id_door"),
			"port":door["realssh"]
		})
		error_msg = "wireguard.gen_configurations: error: scp command returned non-zero code"
		res = run(scp_cmd, error_msg)
		i+=1

	# Clients Configurations Template
	with open(to_root_path("var/template/wg_client.txt"), "r") as temp_file:
		client_temp = Template(temp_file.read())

	i=0
	for dev in conf["device"]:
		# Generate configuration
		conf_filename = "client"+str(i)
		server_id = find_id(conf["door"], dev["node"], "dev")
		client_config = client_temp.substitute({
			"id": i,
			"vm_privkey": cli_privkeys[i],
			"server_pubkey": serv_pubkeys[server_id],
			"server_ip": conf["door"][server_id]["host"]
		})
		# Write configuration to a file
		with open(os.path.join(conf_path, conf_filename), "w") as conf_file:
			conf_file.write(client_config)
		# Copy configuration to the server
		scp_cmd = scp_temp.substitute({
			"file":conf_filename,
			"addr":"10.0.0.2",
			"remote_path":"/etc/wireguard/wg"+i+".conf",
			"key":to_root_path("var/key/id_olim"),
			"port":22
		})
		error_msg = "wireguard.gen_configurations: error: scp command returned non-zero code"
		res = run(scp_cmd, error_msg)
		i+=1

def tunnels(state="up"):
	conf = glob.CONFIG

	ssh_door_key = to_root_path("var/key/id_door")
	ssh_vm_key = to_root_path("var/key/id_olim")

	start_temp = Template("ssh root@${ip} -p ${port} -i ${key} \"wg-quick "+state+" ${wg}\"")

	for door in conf["door"]:
		start_cmd = start_temp.substitute({
			"ip": door["host"],
			"port": door["realssh"],
			"key": ssh_door_key,
			"wg": "/etc/wireguard/wg.conf"
		})
		error_msg = "wireguard.gen_configurations: error: ssh command returned non-zero code"
		res = run(start_cmd, error_msg)

	i=0
	for dev in conf["device"]:
		start_cmd = start_temp.substitute({
			"ip": "10.0.0.2",
			"port": 22,
			"key": ssh_vm_key,
			"wg": "/etc/wireguard/wg"+i+".conf"
		})
		error_msg = "wireguard.gen_configurations: error: ssh command returned non-zero code"
		res = run(start_cmd, error_msg)
		i+=1


def start_tunnels():
	tunnels(state="up")


def start():
	pass


def stop_tunnels():
	tunnels(state="down")


def stop():
	pass


def change_device_server():
	pass