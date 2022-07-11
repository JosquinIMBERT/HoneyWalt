from config import get_conf, set_conf
from utils import eprint, find, markdown_help

def honeywalt_image(options):
	if options.img_cmd == "add":
		image_add(options)
	elif options.img_cmd == "change":
		image_chg(options)
	else:
		image_help()

def image_add(options):
	name = options.name[0]
	username = None if options.user is None else options.user[0]
	password = None if options.password is None else options.password[0]

	conf = get_conf()

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

	conf = get_conf()

	image = find(conf["image"], name, "name")
	if image is None:
		eprint("image change: error: image not found")

	if username is not None:
		image["user"] = username
	if password is not None:
		image["pass"] = password

	set_conf(conf)


def image_help():
	markdown_help("image")
