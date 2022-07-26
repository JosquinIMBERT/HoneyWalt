import sys

def init(conf, vm_priv, vm_pub, door_priv, door_pub):
	# Ports
	global LISTEN_PORTS, BACKEND_PORTS, SOCKET_PORTS
	global CONTROL_PORT, WIREGUARD_PORTS, WG_TCP_PORT
	global WG_UDP_PORT

	# IP
	global VM_IP, CONTROL_IP

	# Keys
	global VM_PRIV_KEY, VM_PUB_KEY, DOOR_PRIV_KEY, DOOR_PUB_KEY

	# Socket
	global VM_SOCK

	# Config
	global CONFIG

	# Miscellaneous
	global LOG_LEVEL, INFO, WARNING, ERROR
	
	LISTEN_PORTS=2000
	BACKEND_PORTS=3000
	SOCKET_PORTS=4000
	CONTROL_PORT=5555
	WIREGUARD_PORTS=6000
	WG_UDP_PORT=51820
	WG_TCP_PORT=51819

	VM_IP = "10.0.0.2"
	CONTROL_IP = "127.0.0.1"

	VM_PRIV_KEY=vm_priv
	VM_PUB_KEY=vm_pub
	DOOR_PRIV_KEY=door_priv
	DOOR_PUB_KEY=door_pub

	VM_SOCK = None

	CONFIG = conf

	LOG_LEVEL = 0
	INFO = 2
	WARNING = 1
	ERROR = 0

def set_log_level(log_level):
	global LOG_LEVEL

	if log_level=="ERROR":
		LOG_LEVEL = ERROR
	elif log_level=="WARNING":
		LOG_LEVEL = WARNING
	elif log_level=="INFO":
		LOG_LEVEL = INFO
	else:
		print("honeywalt: invalid log level")
		sys.exit(1)