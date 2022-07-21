import os, sys, subprocess
from os.path import exists
from string import Template

from utils import *
import glob

# TO BE TESTED: start_tunnels_to_dmz, start, start_tunnels_to_doors


def gen_configurations():
	conf = glob.CONFIG
	i=0
	with open(to_root_path("var/template/cowrie_conf.txt"), "r") as temp_file:
		temp = Template(temp_file.read())
	for dev in conf["device"]:
		img = find(conf["image"], dev["image"], "name")
		if img is None:
			eprint("cowrie.gen_configurations: Error: image not found for device "+dev["node"])
		else:
			backend_user = img["user"]
			backend_pass = img["pass"]
		str_i = str(i)
		download_path = to_root_path("run/cowrie/download/"+str_i+"/")
		if not exists(download_path):
			os.mkdir(download_path)
		params = {
			'log_path' : to_root_path("run/cowrie/log/"+str_i+".log"),
			'download_path' : download_path,
			'listen_port' : glob.LISTEN_PORTS+i,
			'backend_host' : "127.0.0.1",
			'backend_port' : glob.BACKEND_PORTS+i,
			'backend_user' : backend_user,
			'backend_pass' : backend_pass,
			'logfile' : to_root_path("run/cowrie/log/"+str_i+".json"),
			'socket_port' : glob.SOCKET_PORTS+i
		}
		content = temp.substitute(params)
		with open(to_root_path("run/cowrie/conf/"+str(i)+".conf"), "w") as conf_file:
			conf_file.write(content)
		i+=1


def start_tunnels_to_dmz():
	conf = glob.CONFIG
	vm_ip="10.0.0.2"
	i=0
	template = Template("ssh -f -N -M -S ${socket} \
		-L ${port}:${ip}:22 \
		root@${vm_ip} \
		-i ${key_path}")
	for dev in conf["device"]:
		tunnel_cmd = template.substitute({
			"socket": to_root_path("run/ssh/cowrie-dmz/sock"+str(i)),
			"port": glob.BACKEND_PORTS+i,
			"ip": dev["ip"],
			"vm_ip": vm_ip,
			"key_path": glob.VM_PRIV_KEY
		})
		error_msg = "cowrie.start_tunnels_to_dmz: error: ssh command returned non-zero code"
		run(tunnel_cmd, error_msg)
		i+=1


def start():
	conf = glob.CONFIG
	i=0
	template = Template("export COWRIE_CONFIG_PATH=${conf_path}; \
		/home/cowrie/cowrie/bin/cowrie start --pidfile=${pid_path}")
	for dev in conf["device"]:
		cmd = template.substitute({
			"conf_path": to_root_path("run/cowrie/conf/"+str(i)+".conf"),
			"pid_path": to_root_path("run/cowrie/pid/"+str(i)+".pid")
		})
		error_msg = "cowrie.start: error: failed to start cowrie"
		run(cmd, error_msg)
		i+=1


def start_tunnels_to_doors():
	conf = glob.CONFIG
	template = Template("ssh -f -N -M -S ${socket} \
		-R *:${fakessh_port}:127.0.0.1:${exposed_port} \
		-i ${key_path} \
		root@${host} \
		-p ${realssh_port}")
	i=0
	for door in conf["door"]:
		dev_id = find_id(conf["device"], door["dev"], "node")
		tunnel_cmd = template.substitute({
			"socket": to_root_path("run/ssh/cowrie-out/sock"+str(i)),
			"fakessh_port": 22,
			"exposed_port": glob.LISTEN_PORTS+dev_id,
			"key_path": glob.DOOR_PRIV_KEY,
			"host": door["host"],
			"realssh_port": door["realssh"]
		})
		error_msg = "cowrie.start_tunnels_to_doors: error: ssh command returned non-zero code"
		run(tunnel_cmd, error_msg)
		i+=1


def stop_tunnels():
	for p in ["run/ssh/cowrie-dmz", "run/ssh/cowrie-out"]:
		path = to_root_path(p)
		for killpath in os.listdir(path):
			kill_from_file(os.path.join(path, killpath), type="ssh")


def stop():
	path = to_root_path("run/cowrie/pid")
	for pidpath in os.listdir(path):
		kill_from_file(os.path.join(path, pidpath))


def state():
	# code from https://stackoverflow.com/questions/2632205/how-to-count-the-number-of-files-in-a-directory-using-python#2632251
	DIR = to_root_path("run/cowrie/pid")
	nb_pids = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name)) and name.endswith(".pid") and is_pid(os.path.join(DIR, name))])
	return nb_pids