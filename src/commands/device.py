import sys

from config import set_conf
import glob
from utils import *


def honeywalt_device(options):
	if options.dev_cmd == "add":
		device_add(options)
	elif options.dev_cmd == "change":
		device_chg(options)
	elif options.dev_cmd == "del":
		device_del(options)
	elif options.dev_cmd == "show":
		device_show(options)
	else:
		device_help()


def device_add(options):
	name = options.name[0]
	mac_addr = options.mac_addr[0]
	image = options.image[0]

	conf = glob.CONFIG

	if find(conf["device"], name, "node") is not None or \
	   find(conf["device"], mac_addr, "mac") is not None:
		eprint("device add: error: device already exists")
	
	if find(conf["image"], image, "name") is None:
		eprint("device add: error: image not found")

	new_dev = {
		"node":name,
		"image":image,
		"mac":mac_addr
	}
	conf["device"] += [ new_dev ]
	set_conf(conf)


def device_chg(options):
	name = options.name[0]
	new_name = None if options.new_name is None else options.new_name[0]
	new_image = None if options.image is None else options.image[0]
	
	if new_name is None and new_image is None:
		eprint("device change: error: no new value was given")

	conf = glob.CONFIG

	device = find(conf["device"], name, "node")
	if device is None:
		eprint("device change: error: device not found")

	if new_name is not None:
		if find(conf["device"], new_name, "node") is not None:
			eprint("device change: error: the new name for the device is already taken")
		device["node"] = new_name

	if new_image is not None:
		if find(conf["image"], new_image, "name") is None:
			eprint("device change: error: image not found")
		device["image"] = new_image

	set_conf(conf)


def device_del(options):
	dev_name = options.name[0]

	dev_id = find_id(glob.CONFIG["device"], dev_name, "node")
	if dev_id == -1:
		eprint("device del: error: unable to find device "+dev_name)

	door = find(glob.CONFIG["door"], glob.CONFIG["device"][dev_id]["node"], "dev")
	if door is not None:
		eprint("device del: error: door "+door["host"]+" uses device "+dev_name)

	del glob.CONFIG["device"][dev_id]

	set_conf(glob.CONFIG)


def device_show(options):
	conf = glob.CONFIG
	print_object_array(conf["device"], ["node", "mac", "image", "ip"])


def device_help():
	markdown_help("device")
