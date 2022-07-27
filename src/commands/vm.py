import time

import tools.vm as vm
from utils import *
import glob

def honeywalt_vm(options):
	if options.vm_cmd == "shell":
		vm_shell(options)
	elif options.vm_cmd == "start":
		vm_start(options)
	elif options.vm_cmd == "stop":
		vm_stop(options)
	else:
		vm_help()

def vm_shell(options):
	if vm.state() and vm.phase()==1:
		i=0
		while i<24:
			i+=1
			try:
				run("ssh root@10.0.0.2 -i "+glob.VM_PRIV_KEY+" 2>/dev/null", "")
			except:
				if i==1:
					print("Waiting for the VM to boot...")
				time.sleep(5)
			else:
				break
		if i>=24:
			eprint("vm shell: error: failed to connect to the vm")

def vm_start(options):
	if vm.state():
		eprint("vm start: error: the VM is already running")
	phase = options.phase[0]
	vm.start(phase)

def vm_stop(options):
	if not vm.state():
		wprint("vm stop: the VM is already stopped")
	else:
		vm.stop()

def vm_help():
	markdown_help("vm")