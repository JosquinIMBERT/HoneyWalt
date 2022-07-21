import os, signal
from os.path import exists

import glob
from utils import *

# TO BE TESTED: start and stop

def start(phase):
	with open(to_root_path("var/template/vm_phase"+str(phase)+".txt"), "r") as temp_file:
		template = Template(temp_file.read())
	vm_cmd = template.substitute({
		"pidfile": to_root_path("run/vm.pid"),
		"diskfile": "/persist/disk.dd",
		"swapfile": "/persist/swap.dd",
		"wimgfile": "/persist/wimg.dd",
		"tapout-up": to_root_path("src/script/tapout-up.sh"),
		"tapout-down": to_root_path("src/script/tapout-down.sh"),
		"control_port": glob.CONTROL_PORT
	})
	res = subprocess.run(vm_cmd, shell=True ,check=True, text=True)
	if res.returncode != 0:
		eprint("Error: failed to start the VM")


def state():
	pidpath = to_root_path("run/vm.pid")
	return is_pid(pidpath)


def stop():
	path = to_root_path("run/vm.pid")
	if exists(path):
		kill_from_file(path)