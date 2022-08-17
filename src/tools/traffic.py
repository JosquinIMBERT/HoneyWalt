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
	run(command, "failed to stop control")