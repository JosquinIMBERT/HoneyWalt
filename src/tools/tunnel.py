import os, tempfile
from string import Template

from utils import *
import glob




#################
## START UTILS ##
#################

def gen_sock_filename(directory):
	# Warning: using a __deprecated__ function
	# May need to be changed, but I think the ssh
	# command expects that the file doesn't exist
	socketfile = tempfile.mktemp(".sock", "", dir=socketdir)
	try:
		os.remove(socketfile)
	except OSError:
		pass
	return socketfile

def start_tunnel_door_controller(socketdir, door_port, local_port, door):
	toDoor_template = Template("ssh -f -N -M -S ${socket} \
		-R *:${door_port}:127.0.0.1:${local_port} \
		-i ${key_path} \
		root@${host} \
		-p ${realssh_port}")

	tunnel_cmd = template.substitute({
		"socket": gen_sock_filename(socketdir),
		"door_port": door_port,
		"local_port": local_port,
		"key_path": glob.DOOR_PRIV_KEY,
		"host": door["host"],
		"realssh_port": door["realssh"]
	})
	error_msg = "failed to start tunnel between door and controller"
	run(tunnel_cmd, error_msg)

def start_tunnel_controller_dmz(socketdir, local_port, dev_ip, dev_port):
	toDMZ_template = Template("ssh -f -N -M -S ${socket} \
		-L ${local_port}:${ip}:${dev_port} \
		root@${vm_ip} \
		-i ${key_path}")

	tunnel_cmd = toDMZ_template.substitute({
		"socket": gen_sock_filename(socketdir),
		"local_port": local_port,
		"ip": dev_ip,
		"dev_port": dev_port,
		"vm_ip": glob.VM_IP,
		"key_path": glob.VM_PRIV_KEY
	})




###########
## START ##
###########

def start_exposure_tunnels():
	for dev in glob.CONFIG["device"]:
		door = find(glob.CONFIG["door"], dev["node"], "dev")
		for port in dev["ports"]:
			# Controller --> Device
			start_tunnel_controller_dmz(
				to_root_path("run/ssh/expose-dmz/"),
				glob.EXPOSE_PORTS+i,
				dev["ip"],
				port
			)
			# Door --> Controller
			start_tunnel_door_controller(
				to_root_path("run/ssh/expose-out/"),
				port,
				glob.EXPOSE_PORTS+i,
				door
			)
			i+=1

def start_cowrie_tunnels_out():
	i=0
	for door in glob.CONFIG["door"]:
		dev_id = find_id(glob.CONFIG["device"], door["dev"], "node")
		start_tunnel_door_controller(
			to_root_path("run/ssh/cowrie-out/"),
			22,
			glob.LISTEN_PORTS+dev_id,
			door
		)
		i+=1

def start_cowrie_tunnels_dmz():
	i=0
	for dev in glob.CONFIG["device"]:
		start_tunnel_controller_dmz(
			to_root_path("run/ssh/cowrie-dmz/"),
			glob.BACKEND_PORTS+i,
			dev["ip"],
			22
		)
		i+=1




###########
## CLOSE ##
###########

def stop_tunnels(directory):
	path = to_root_path("run/ssh/"+directory)
	for killpath in os.listdir(path):
		if killpath.endswith(".sock"):
			try:
				kill_from_file(os.path.join(path, killpath), filetype="ssh")
			except:
				log(
					glob.WARNING,
					"Failed to close a SSH tunnel. The control socket is: "+str(killpath)
				)

def stop_exposure_tunnels():
	for directory in ["expose-out", "expose-dmz"]:
		stop_tunnels(directory)

def stop_cowrie_tunnels_out():
	stop_tunnels("cowrie-out")

def stop_cowrie_tunnels_dmz():
	stop_tunnels("cowrie-dmz")