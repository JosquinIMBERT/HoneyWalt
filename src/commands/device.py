import sys, re

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
	ports = [] if options.ports is None else [int(port) for port in options.ports[0].split(",")]
	conf = glob.CONFIG

	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if regex.match(image):
		log(glob.WARNING, image+" seem to be a cloneable image link. Extracting short name")
		image = extract_short_name(image)

	if find(conf["device"], name, "node") is not None or \
	   find(conf["device"], mac_addr, "mac") is not None:
		eprint("device already exists")
	
	if find(conf["image"], image, "short_name") is None:
		eprint("image not found")

	new_dev = {
		"node":name,
		"image":image,
		"mac":mac_addr,
		"ports":ports
	}
	conf["device"] += [ new_dev ]
	set_conf(conf)


def device_chg(options):
	name = options.name[0]
	new_name = None if options.new_name is None else options.new_name[0]
	new_image = None if options.image is None else options.image[0]
	new_ports = None if options.ports is None else [int(port) for port in options.ports[0].split(",")]

	if new_image:
		regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
		if regex.match(new_image):
			log(glob.WARNING, new_image+" seem to be a cloneable image link. Extracting short name")
			new_image = extract_short_name(new_image)

	conf = glob.CONFIG

	device = find(conf["device"], name, "node")
	if device is None:
		eprint("device not found")

	if new_name is not None:
		if find(conf["device"], new_name, "node") is not None:
			eprint("the new name for the device is already taken")
		device["node"] = new_name

	if new_image is not None:
		if find(conf["image"], new_image, "name") is None:
			eprint("image not found")
		device["image"] = new_image

	if new_ports is not None:
		device["ports"] = new_ports

	set_conf(conf)


def device_del(options):
	dev_name = options.name[0]

	dev_id = find_id(glob.CONFIG["device"], dev_name, "node")
	if dev_id == -1:
		eprint("unable to find device "+dev_name)

	door = find(glob.CONFIG["door"], glob.CONFIG["device"][dev_id]["node"], "dev")
	if door is not None:
		eprint("door "+door["host"]+" uses device "+dev_name)

	del glob.CONFIG["device"][dev_id]

	set_conf(glob.CONFIG)


def device_show(options):
	conf = glob.CONFIG
	print_object_array(conf["device"], ["node", "mac", "image", "ip", "ports"])


def device_help():
	markdown_help("device")
