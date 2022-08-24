import os, signal, subprocess
from os.path import exists
from string import Template

import glob
from utils import *

def start(phase):
	with open(to_root_path("run/vm.phase"), "w") as file:
		file.write(str(phase))
	with open(to_root_path("var/template/vm_phase"+str(phase)+".txt"), "r") as temp_file:
		template = Template(temp_file.read())
	vm_cmd = template.substitute({
		"pidfile": to_root_path("run/vm.pid"),
		"diskfile": "/persist/disk.dd",
		"swapfile": "/persist/swap.dd",
		"wimgfile": "/persist/wimg.dd",
		"tapout_up": to_root_path("src/script/tapout-up.sh"),
		"tapout_down": to_root_path("src/script/tapout-down.sh")
	})
	run(vm_cmd, "failed to start the VM")


def state():
	pidpath = to_root_path("run/vm.pid")
	return is_pid(pidpath)


def phase():
	with open(to_root_path("run/vm.phase"), "r") as file:
		phase = file.read()
	return int(phase)


def stop():
	# Trying soft shutdown (run shutdown command)
	try:
		vm_run("init 0", timeout=10)
		return
	except subprocess.TimeoutExpired:
		log(glob.WARNING, "soft shutdown failed. Starting hard shutdown.")

	# Hard shutdown (kill qemu process)
	path = to_root_path("run/vm.pid")
	if exists(path):
		try:
			kill_from_file(path)
			return
		except:
			pass
	log(
		glob.WARNING,
		"Failed to stop the VM (pidfile:"+str(path)+")."
	)