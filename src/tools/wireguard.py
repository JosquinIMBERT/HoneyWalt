import subprocess
from string import Template

import glob
from utils import *


# Generate the (public and private) keys of the wireguard servers and clients
# May be it could be simplified (we may not neet to generate the keys on the
# host that will use it)
def gen_keys():
	# Key generation template
	keygen_cmd = "umask 077; \
		wg genkey >privkey; \
		wg pubkey <privkey >pubkey; \
		cat privkey; \
		cat pubkey"

	# Servers keys
	serv_privkeys = []
	serv_pubkeys = []
	for door in glob.CONFIG["door"]:
		error_msg = "wireguard.gen_keys: ssh command returned non-zero code"
		res = door_run(door, keygen_cmd, err=error_msg, output=True)
		privkey, pubkey = res.split("\n", 1)
		serv_privkeys += [ privkey ]
		serv_pubkeys += [ pubkey ]

	# Clients keys
	cli_privkeys = []
	cli_pubkeys = []
	for dev in glob.CONFIG["device"]:
		error_msg = "wireguard.gen_keys: ssh command returned non-zero code"
		res = vm_run(keygen_cmd, err=error_msg, output=True)
		privkey, pubkey = res.split("\n", 1)
		cli_privkeys += [ privkey ]
		cli_pubkeys += [ pubkey ]

	return serv_privkeys, serv_pubkeys, cli_privkeys, cli_pubkeys


def del_configurations():
	# Local
	path = to_root_path("run/wireguard")
	delete(path, suffix=".conf")
	# VM
	error_msg = "wireguard:del_configurations: failed to delete vm configurations"
	vm_run("rm -f /etc/wireguard/*", err=error_msg)


def gen_configurations(serv_privkeys, serv_pubkeys, cli_privkeys, cli_pubkeys):
	del_configurations()
	# General variables
	conf_path = to_root_path("run/wireguard/")
	scp_temp = Template("scp -i ${key} -P ${port} "+conf_path+"${file} root@${addr}:${remote_path}")

	# Server Configuration Templates
	with open(to_root_path("var/template/wg_server_itf.txt"), "r") as temp_file:
		server_itf_temp = Template(temp_file.read())
	with open(to_root_path("var/template/wg_server_peer.txt"), "r") as temp_file:
		server_peer_temp = Template(temp_file.read())

	i=0
	for door in glob.CONFIG["door"]:
		# Generate Configuration
		conf_filename = "server"+str(i)+".conf"
		server_config = server_itf_temp.substitute({
			"server_privkey": serv_privkeys[i]
		})
		for cli_pubkey in cli_pubkeys:
			server_config += "\n\n" + server_peer_temp.substitute({
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
			"key":glob.DOOR_PRIV_KEY,
			"port":door["realssh"]
		})
		error_msg = "wireguard.gen_configurations: scp command returned non-zero code"
		run(scp_cmd, error_msg)
		i+=1

	# Clients Configurations Template
	with open(to_root_path("var/template/wg_client.txt"), "r") as temp_file:
		client_temp = Template(temp_file.read())

	i=0
	for dev in glob.CONFIG["device"]:
		# Generate configuration
		conf_filename = "client"+str(i)+".conf"
		server_id = find_id(glob.CONFIG["door"], dev["node"], "dev")
		client_config = client_temp.substitute({
			"table": glob.WIREGUARD_PORTS+i,
			"dev_ip": dev["ip"],
			"id": i,
			"vm_privkey": cli_privkeys[i],
			"server_pubkey": serv_pubkeys[server_id],
			"server_ip": glob.CONFIG["door"][server_id]["host"]
		})
		# Write configuration to a file
		with open(os.path.join(conf_path, conf_filename), "w") as conf_file:
			conf_file.write(client_config)
		# Copy configuration to the server
		scp_cmd = scp_temp.substitute({
			"file":conf_filename,
			"addr":"10.0.0.2",
			"remote_path":"/etc/wireguard/wg"+str(i)+".conf",
			"key":glob.VM_PRIV_KEY,
			"port":22
		})
		error_msg = "wireguard.gen_configurations: scp command returned non-zero code"
		run(scp_cmd, error_msg)
		i+=1


def tunnels(state="up"):
	start_temp = Template("wg-quick "+state+" ${wg}")

	wg_cmd = "wg-quick "+state+" /etc/wireguard/wg.conf"
	for door in glob.CONFIG["door"]:
		error_msg = "wireguard.gen_configurations: ssh command returned non-zero code"
		door_run(door, wg_cmd, err=error_msg)

	i=0
	for dev in glob.CONFIG["device"]:
		wg_cmd = "wg-quick "+state+" /etc/wireguard/wg"+str(i)+".conf"
		error_msg = "wireguard.gen_configurations: ssh command returned non-zero code"
		vm_run(wg_cmd, err=error_msg)
		i+=1


def start_tunnels():
	tunnels(state="up")


def start_tcp_tunnels():
	udp_ip = "127.0.0.1"
	udp_port = glob.WG_UDP_PORT
	tcp_host = "0.0.0.0"
	tcp_port = glob.WG_TCP_PORT
	door_args = udp_ip+" "+str(udp_port)+" "+tcp_host+" "+str(tcp_port)
	door_cmd = "python3 /root/wg_tcp_adapter.py /root/tunnel.pid door "+door_args+" &"
	for door in glob.CONFIG["door"]:
		# https://stackoverflow.com/questions/18569588/ssh-remote-command-does-not-return
		# It seems like the only way to run the program in background is to also keep the ssh connection locally in background
		# Anyway the local process will be killed when the remote process will be killed
		door_run(door, door_cmd, background=True)

	i=0
	for dev in glob.CONFIG["device"]:
		udp_lo_host="0.0.0.0"
		udp_lo_port=glob.WIREGUARD_PORTS+i
		tcp_host=find(glob.CONFIG["door"], dev["node"], "dev")["host"]
		tcp_port=glob.WG_TCP_PORT
		local_args = udp_lo_host+" "+str(udp_lo_port)+" "+tcp_host+" "+str(tcp_port)
		prog = to_root_path("src/tools/wg_tcp_adapter.py")
		pid_file = to_root_path("run/wg_tcp_adapter/tunnel"+str(i)+".pid")
		local_cmd = "python3 "+prog+" "+pid_file+" controller "+local_args+" &"
		run(local_cmd, "failed to start udp/tcp adapter")
		i+=1


def stop_tunnels():
	tunnels(state="down")


def stop_tcp_tunnels():
	for door in glob.CONFIG["door"]:
		door_run(door, "kill $(cat /root/tunnel.pid)")
	path = to_root_path("run/wg_tcp_adapter")
	for pidpath in os.listdir(path):
		kill_from_file(os.path.join(path, pidpath))


def change_device_server():
	# TODO
	pass