from utils import *

def start_control():
	dev = "tap-out"
	latency = glob.CONFIG["controller"]["latency"]
	throughput = glob.CONFIG["controller"]["throughput"]
	nb_ports = len(glob.CONFIG["door"])
	ports_list = range(glob.WIREGUARD_PORTS, glob.WIREGUARD_PORTS+nb_ports)
	ports_list = [str(p) for p in ports_list]
	ports = ",".join(ports_list)

	prog = to_root_path("src/script/control-up.sh")
	args = dev+" "+glob.IP_FOR_DMZ+" "+latency+" "+throughput+" "+ports
	command = prog+" "+args
	run(command, "failed to start control")

def stop_control():
	prog = to_root_path("src/script/control-down.sh")
	command = prog+" tap-out"
	try:
		run(command, "failed to stop control")
	except:
		log(glob.WARNING,"Failed to stop traffic control.")

def start_door_firewall():
	public_ip = get_public_ip()
	for door in glob.CONFIG["door"]:
		door_run(door, "/root/HoneyWalt_door/firewall-up.sh "+str(public_ip), "Failed to start door firewall")

def stop_door_firewall():
	for door in glob.CONFIG["door"]:
		try:
			door_run(door, "/root/HoneyWalt_door/firewall-down.sh", "Failed to stop door firewall")
		except:
			log(glob.WARNING,"Failed to stop door firewall (door: "+str(door["host"])+").")