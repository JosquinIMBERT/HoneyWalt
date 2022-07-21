import sys

from config import set_conf
import glob
from utils import *


def honeywalt_door(options):
	if options.door_cmd == "add":
		door_add(options)
	elif options.door_cmd == "change":
		door_chg(options)
	elif options.door_cmd == "del":
		door_del(options)
	elif options.door_cmd == "show":
		door_show(options)
	else:
		door_help()


def door_pubkey_instructions():
	print("Before to use it, you should copy the following public key to your door's .ssh/authorized_keys file for root:")
	with open(glob.DOOR_PUB_KEY) as file:
		key = file.read()
		print(key)
		file.close()


def door_add(options):
	ip = str(options.ip[0])
	dev = str(options.dev[0])

	conf = glob.CONFIG

	# Check device (the device should be registered first)
	device = find(conf["device"], dev, "node")
	if device is None:
		eprint("door add: error: device not found")

	# Check door doesn't exist
	door = find(conf["door"], ip, "host")
	if door is not None:
		eprint("door add: error: door already exists")

	# Add the door
	new_door = {
		"host":ip,
		"realssh":1312,
		"dev":dev
	}
	conf["door"] += [ new_door ]
	set_conf(conf)

	print("-> The door was added")

	# Show instructions
	door_pubkey_instructions()


def door_chg(options):
	ip = options.ip[0]
	new_ip = None if options.ip_address is None else options.ip_address[0]
	new_dev = None if options.device is None else options.device[0]
	if new_ip is None and new_dev is None:
		eprint("door change: error: no new value was given")
	
	conf = glob.CONFIG

	# Find the door
	door = find(conf["door"], ip, "host")
	if door is None:
		eprint("door change: error: door not found")

	# Update the fields
	if new_ip is not None:
		door["host"] = new_ip
	if new_dev is not None:
		door["dev"] = new_dev

	# Write on the file
	set_conf(conf)

	# Show instructions
	if new_ip is not None:
		door_pubkey_instructions()


def door_del(options):
	ip = options.ip[0]

	conf = glob.CONFIG

	# Find the door
	door = find_id(conf["door"], ip, "host")
	if door == -1:
		eprint("door change: error: door not found")

	del conf["door"][door]
	
	set_conf(conf)


def door_show(options):
	conf = glob.CONFIG
	print_object_array(conf["door"], ["host","dev"])


def door_help():
	markdown_help("door")