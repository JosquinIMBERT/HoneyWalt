from config import set_conf
import glob
from utils import eprint, find, markdown_help, print_object_array

def honeywalt_image(options):
	if options.img_cmd == "add":
		image_add(options)
	elif options.img_cmd == "change":
		image_chg(options)
	elif options.img_cmd == "del":
		image_del(options)
	elif options.img_cmd == "show":
		image_show(options)
	else:
		image_help()

def image_add(options):
	name = options.name[0]
	username = None if options.user is None else options.user[0]
	password = None if options.password is None else options.password[0]

	conf = glob.CONFIG

	if find(conf["image"], name, "name") is not None:
		eprint("image add: error: image already exists")

	if username is None:
		print("No username was given. Using username: root, password: root")
		username = "root"
		password = "root"
	elif password is None:
		print("No password was given. Using password: "+username)
		password = username

	new_img = {
		"name":name,
		"user":username,
		"pass":password
	}
	conf["image"] += [ new_img ]
	set_conf(conf)

def image_chg(options):
	name = options.name[0]
	username = None if options.user is None else options.user[0]
	password = None if options.password is None else options.password[0]

	if username is None and password is None:
		eprint("image change: error: no new value was given")

	conf = glob.CONFIG

	image = find(conf["image"], name, "name")
	if image is None:
		eprint("image change: error: image not found")

	if username is not None:
		image["user"] = username
	if password is not None:
		image["pass"] = password

	set_conf(conf)


def image_del(options):
	print("TODO")


def image_show(options):
	conf = glob.CONFIG
	print_object_array(conf["image"], ["name", "user", "pass"])


def image_help():
	markdown_help("image")
