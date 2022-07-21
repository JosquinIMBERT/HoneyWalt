import glob
import tools.cowrie as cowrie
import tools.traffic as traffic
import tools.vm as vm
import tools.wireguard as wg

# Start HoneyWalt
def honeywalt_start(options):
	# Generate cowrie configuration files
	regen = not options.no_regen
	if regen:
		cowrie.gen_configurations()

	# Start the VM
	vm.start(2)
	glob.VM_SOCK = ControlSocket(2)
	conf = glob.CONFIG
	wg_ports = []
	backends = []
	i=0
	for dev in conf["device"]:
		wg_ports += [ glob.WIREGUARD_PORTS+i ]
		backends += [ dev["node"] ]
		i+=1
	ips = glob.VM_SOCK.initiate(ports=wg_ports, backends=backends)

	if regen:
		serv_privkeys, serv_pubkeys, cli_privkeys, cli_pubkeys = wireguard.gen_keys()
		wireguard.gen_configurations(
			serv_privkeys,
			serv_pubkeys,
			cli_privkeys,
			cli_pubkeys,
			ips
		)
	
	# Start tunnels between cowrie and devices
	cowrie.start_tunnels_to_dmz(ips)

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
	vm.start(1)
	sock = ControlSocket(1)
	conf = glob.CONFIG
	img_name = []
	img_user = []
	img_pass = []
	for img in conf["image"]:
		img_name += [ img["name"] ]
		img_user += [ img["user"] ]
		img_pass += [ img["pass"] ]
	sock.initiate(images=img_name, usernames=img_user, passwords=img_pass)
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

def honeywalt_status(options):
	pass
	# TODO