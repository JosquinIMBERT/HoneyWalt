import os, sys, subprocess
from os.path import exists
from string import Template

from utils import *
import glob


def del_configurations():
	path = to_root_path("run/cowrie/conf")
	delete(path, suffix=".conf")


def gen_configurations():
	del_configurations()
	conf = glob.CONFIG
	i=0
	with open(to_root_path("var/template/cowrie_conf.txt"), "r") as temp_file:
		temp = Template(temp_file.read())
	for dev in conf["device"]:
		img = find(conf["image"], dev["image"], "short_name")
		if img is None:
			eprint("image not found for device "+dev["node"])
		backend_user = img["user"]
		backend_pass = img["pass"]
		str_i = str(i)
		download_path = to_root_path("run/cowrie/download/"+str_i+"/")
		if not exists(download_path):
			os.mkdir(download_path)
		params = {
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


def start():
	conf = glob.CONFIG
	i=0
	with open(to_root_path("var/template/start_cowrie.txt"), "r") as file:
		template = Template(file.read())
	for dev in conf["device"]:
		cmd = template.substitute({
			"conf_path": to_root_path("run/cowrie/conf/"+str(i)+".conf"),
			"pid_path": to_root_path("run/cowrie/pid/"+str(i)+".pid"),
			"log_path": to_root_path("run/cowrie/log/"+str(i)+".log")
		})
		error_msg = "failed to start cowrie"
		run(cmd, error_msg)
		i+=1


def stop():
	path = to_root_path("run/cowrie/pid")
	for pidpath in os.listdir(path):
		if pidpath.endswith(".pid"):
			kill_from_file(os.path.join(path, pidpath))


def state():
	# code from https://stackoverflow.com/questions/2632205/how-to-count-the-number-of-files-in-a-directory-using-python#2632251
	DIR = to_root_path("run/cowrie/pid")
	nb_pids = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name)) and name.endswith(".pid") and is_pid(os.path.join(DIR, name))])
	return nb_pids