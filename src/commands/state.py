import time

from config import set_conf
import glob
import tools.cowrie as cowrie
import tools.traffic as traffic
import tools.vm as vm
import tools.wireguard as wg
from utils import *
from control_socket import ControlSocket


# Start HoneyWalt
def honeywalt_start(options):
	if is_running():
		eprint("honeywalt_start: error: please stop HoneyWalt before to start")

	# Check if changes were commited
	if glob.CONFIG["need_commit"] == "Empty":
		eprint("Your configuration is empty")
	elif glob.CONFIG["need_commit"] == "True":
		eprint("You need to commit your configuration before to run HoneyWalt")

	delete(to_root_path("run/cowrie/pid"), suffix=".pid")
	delete(to_root_path("run/ssh/cowrie-dmz"), suffix=".pid")
	delete(to_root_path("run/ssh/cowrie-out"), suffix=".pid")
	delete(to_root_path("run/wg_tcp_adapter"), suffix=".pid")

	# Allow cowrie user to access cowrie files
	run("chown -R cowrie "+to_root_path("run/cowrie/"), "honeywalt start: error: failed chown cowrie")

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
	wg.start_tunnels()
	wg.start_tcp_tunnels()

	# Start traffic control
	traffic.start_control()

	# Start tunnels between cowrie and doors
	cowrie.start_tunnels_to_doors()


# Commit some persistent information on the VM so it is taken
# into acount on the next boot
def honeywalt_commit(options, force=False):
	if is_running():
		eprint("honeywalt_commit: error: please stop HoneyWalt before to commit")

	if glob.CONFIG["need_commit"] == "Empty":
		eprint("Your configuration is empty")
	elif glob.CONFIG["need_commit"] == "False" and not force:
		eprint("Nothing new to commit")

	# Generate cowrie configuration files
	if hasattr(options, "no_regen"):
		regen = not options.no_regen
	else:
		regen = True
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
		serv_privkeys, serv_pubkeys, cli_privkeys, cli_pubkeys = wg.gen_keys()
		wg.gen_configurations(
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
	wg.stop_tcp_tunnels()
	wg.stop_tunnels()
	vm.stop()
	traffic.stop_control()


def honeywalt_restart(options):
	honeywalt_stop(None)

	# Generate configuration files
	regen = options.force_regen
	if regen:
		honeywalt_commit(None, force=True)

	honeywalt_start(None)


def honeywalt_status(options):
	cowrie.del_configurations()
	# VM
	vm_pid = vm.state()
	if vm_pid is not None:
		print("The VM is running with pid "+vm_pid)
	else:
		print("The VM is not running")
	
	# Cowrie
	nb_cowrie_pids = cowrie.state()
	print("There are "+str(nb_cowrie_pids)+" running instance(s) of cowrie")
	
	# Configuration
	nb_devs = len(glob.CONFIG["device"])
	nb_doors= len(glob.CONFIG["door"])
	print("There are "+str(nb_doors)+" door(s) and "+str(nb_devs)+" device(s)")


# We consider the state of the VM determines whether HoneyWalt is running or not
def is_running():
	return vm.state() is not None