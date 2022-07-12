from string import Template

import glob


def gen_keys():
	conf = glob.CONFIG

	# Key generation template
	keygen_cmd = "umask 077; \
		wg genkey >privkey; \
		wg pubkey <privkey >pubkey; \
		cat privkey; \
		cat pubkey"
	keygen_temp = Template("ssh root@${door_ip} -i {keypath} -p {door_port} -c \"${command}\"")

	# Servers keys
	serv_privkeys = []
	serv_pubkeys = []
	ssh_door_key = to_root_path("var/key/id_door")
	for door in conf["door"]:
		# Generate wireguard keys
		command = keygen_temp.substitute({
			"door_ip":door["host"],
			"keypath":ssh_door_key,
			"door_port":door["realssh"],
			"command":keygen_cmd
		})
		print("Generate wireguard keys")
		res = subprocess.run(tunnel_cmd, shell=True ,check=True, text=True, capture_output=True)
		if res.returncode != 0:
			eprint("wireguard.gen_configurations: error: ssh command returned non-zero code")
		output = str(res.stdout)
		privkey, pubkey = output.split("\n", 1)
		serv_privkeys += [ privkey ]
		serv_pubkeys += [ pubkey ]

	cli_privkey = []
	cli_pubkey = []
	for dev in conf["device"]:
		print(dev["node"])

		# Generate wireguard keys
		print("Generate wireguard keys")


def gen_configurations():
	conf = glob.CONFIG

	# Servers Configurations Template
	with open(to_root_path("var/template/wg_server.txt"), "r") as temp_file:
		server_temp = Template(temp_file.read())

	# Clients Configurations Template
	with open(to_root_path("var/template/wg_client.txt"), "r") as temp_file:
		client_temp = Template(temp_file.read())

	for door in conf["door"]:
		# Edit wireguard configuration
		print("Edit wireguard configuration")

	for dev in conf["device"]:
		# Edit wireguard configuration
		print("Edit wireguard configuration")

def start_tunnels():
	pass


def start():
	pass


def stop():
	pass