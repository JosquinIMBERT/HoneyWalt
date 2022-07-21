from config import set_conf
import glob
import tools.cowrie as cowrie
import tools.traffic as traffic
import tools.vm as vm
import tools.wireguard as wg
from utils import *

# Start HoneyWalt
def honeywalt_start(options):
	# Check if changes were commited
	if glob.CONFIG["need_commit"] == "Empty":
		eprint("Your configuration is empty")
	elif glob.CONFIG["need_commit"] == "True":
		eprint("You need to commit your configuration before to run HoneyWalt")

	# Start the VM
	vm.start(2)
	glob.VM_SOCK = ControlSocket(2)
	wg_ports = []
	backends = []
	i=0
	for dev in glob.CONFIG["device"]:
		wg_ports += [ glob.WIREGUARD_PORTS+i ]
		backends += [ dev["node"] ]
		i+=1
	glob.VM_SOCK.initiate()
	
	# Start tunnels between cowrie and devices
	cowrie.start_tunnels_to_dmz()

	# Start cowrie
	cowrie.start()

	# Start wireguard
	wg.start_ssh_tunnels()
	wg.start_tunnels()

	# Start traffic control
	traffic.start_control()

	# Start tunnels between cowrie and doors
	cowrie.start_tunnels_to_doors()


# Commit some persistent information on the VM so it is taken
# into acount on the next boot
def honeywalt_commit(options):
	if glob.CONFIG["need_commit"] == "Empty":
		eprint("Your configuration is empty")
	elif glob.CONFIG["need_commit"] == "False":
		eprint("Nothing new to commit")

	# Generate cowrie configuration files
	regen = not options.no_regen
	if regen:
		cowrie.gen_configurations()

	vm.start(1)
	glob.VM_SOCK = ControlSocket(1)
	img_name = []
	img_user = []
	img_pass = []
	for img in glob.CONFIG["image"]:
		img_name += [ img["name"] ]
		img_user += [ img["user"] ]
		img_pass += [ img["pass"] ]
	devs = []
	for dev in glob.CONFIG["device"]:
		devs += [ dev["node"] ]
	ips = glob.VM_SOCK.initiate(backends=devs, images=img_name, usernames=img_user, passwords=img_pass)

	i=0
	for dev in glob.CONFIG["device"]:
		dev["ip"] = ips[i]
		i+=1
	
	# Generate and distribute wireguard configurations
	if regen:
		serv_privkeys, serv_pubkeys, cli_privkeys, cli_pubkeys = wireguard.gen_keys()
		wireguard.gen_configurations(
			serv_privkeys,
			serv_pubkeys,
			cli_privkeys,
			cli_pubkeys
		)

	set_conf(glob.CONFIG, need_commit=False)

	vm.stop()

def honeywalt_stop(options):
	cowrie.stop_tunnels()
	cowrie.stop()
	wg.stop()
	vm.stop()
	traffic.stop_control()

def honeywalt_restart(options):
	pass
	# TODO

def honeywalt_status(options, show=True):
	# VM
	vm_pid = vm.state()
	if show:
		if vm_pid is not None:
			print("The VM is running with pid "+vm_pid)
		print("The VM is not running")
	
	# Cowrie
	nb_cowrie_pids = cowrie.state()
	if show:
		print("There are "+str(nb_cowrie_pids)+" running instance(s) of cowrie")
	
	# Configuration
	nb_devs = len(glob.CONFIG["device"])
	nb_doors= len(glob.CONFIG["door"])
	if show:
		print("There are "+str(nb_doors)+" door(s) and "+str(nb_devs)+" device(s)")

	# Return true if it is running
	return vm_pid is not None and nb_cowrie_pids>0 and nb_devs>0 and nb_doors>0