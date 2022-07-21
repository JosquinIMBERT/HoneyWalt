from config import get_conf
from utils import *

def init():
	# Ports
	global LISTEN_PORTS, BACKEND_PORTS, SOCKET_PORTS, CONTROL_PORT, WIREGUARD_PORTS

	# IP
	global VM_IP

	# Keys
	global VM_PRIV_KEY, VM_PUB_KEY, DOOR_PRIV_KEY, DOOR_PUB_KEY

	# Socket
	global VM_SOCK

	# Config
	global CONFIG
	
	LISTEN_PORTS=2000
	BACKEND_PORTS=3000
	SOCKET_PORTS=4000
	CONTROL_PORT=5555
	WIREGUARD_PORTS=6000

	VM_IP = "10.0.0.2"

	VM_PRIV_KEY=to_root_path("var/key/id_olim")
	VM_PUB_KEY=to_root_path("var/key/id_olim.pub")
	DOOR_PRIV_KEY=to_root_path("var/key/id_door")
	DOOR_PUB_KEY=to_root_path("var/key/id_door.pub")

	VM_SOCK = None

	CONFIG = get_conf()