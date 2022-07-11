import sys

from config import get_conf, set_conf
from utils import eprint, find, markdown_help


def honeywalt_device(options):
	if options.dev_cmd == "add":
		device_add(options)
	elif options.dev_cmd == "change":
		device_chg(options)
	else:
		device_help()


def device_add(options):
	name = options.name[0]
	mac_addr = options.mac_addr[0]
	image = options.image[0]

	conf = get_conf()

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

	conf = get_conf()

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


def device_help():
	markdown_help("device")
