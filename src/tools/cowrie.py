import os, sys, subprocess
from os.path import exists

from config import get_conf
from string import Template
from utils import eprint, find, find_id, to_root_path
import glob

# TO BE TESTED: start_tunnels_to_dmz, start, start_tunnels_to_doors

def gen_configurations():
	conf = get_conf()
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

def start_tunnels_to_dmz(ips):
	conf = get_conf()
	vm_ip="10.0.0.2"
	key_path = to_root_path("var/key/id_olim")
	i=0
	template = Template("ssh -f -N -L ${port}:${ip}:22 root@${vm_ip} -i ${key_path}")
	for dev in conf["device"]:
		tunnel_cmd = template.substitute({
			"port": glob.BACKEND_PORTS+i,
			"ip": ips[i],
			"vm_ip": vm_ip,
			"key_path": key_path
		})
		res = subprocess.run(tunnel_cmd, shell=True ,check=True, text=True)
		if res.returncode != 0:
			eprint("cowrie.start_tunnels_to_dmz: error: ssh command returned non-zero code")
		i+=1

def start():
	conf = get_conf()
	i=0
	template = Template("export COWRIE_CONFIG_PATH=${conf_path}; \
		/home/cowrie/cowrie/bin/cowrie start --pidfile=${pid_path}")
	for dev in conf["device"]:
		cmd = template.substitute({
			"conf_path": to_root_path("run/cowrie/conf/"+str(i)+".conf"),
			"pid_path": to_root_path("run/cowrie/pid/"+str(i)+".pid")
		})
		res = subprocess.run(cmd, shell=True ,check=True, text=True)
		if res.returncode != 0:
			eprint("cowrie.start: error: failed to start cowrie")
		i+=1

def start_tunnels_to_doors():
	conf = get_conf()
	key_path = to_root_path("var/key/id_door")
	template = Template("ssh -f -N -R *:${fakessh_port}:127.0.0.1:${exposed_port} \
		-i ${key_path} \
		root@${host} \
		-p ${realssh_port}")
	i=0
	for door in conf["door"]:
		dev_id = find_id(conf["device"], door["dev"], "node")
		tunnel_cmd = template.substitute({
			"fakessh_port": 22,
			"exposed_port": glob.LISTEN_PORTS+dev_id,
			"key_path": key_path,
			"host": door["host"],
			"realssh_port": door["realssh"]
		})
		res = subprocess.run(tunnel_cmd, shell=True ,check=True, text=True)
		if res.returncode != 0:
			eprint("cowrie.start_tunnels_to_doors: error: ssh command returned non-zero code")
			sys.exit(1)
		i+=1