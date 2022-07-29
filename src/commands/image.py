from config import set_conf
import glob
from utils import *

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

	# TODO: at some point, we need a cloneable image link for walt
	#regex = re.compile("(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?")
	#if not regex.match(name):
    #    eprint(name+" is not an image clonable link")

	conf = glob.CONFIG

	if find(conf["image"], name, "name") is not None:
		eprint("image already exists")

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
		eprint("no new value was given")

	conf = glob.CONFIG

	image = find(conf["image"], name, "name")
	if image is None:
		eprint("image not found")

	if username is not None:
		image["user"] = username
	if password is not None:
		image["pass"] = password

	set_conf(conf)


def image_del(options):
	img_name = options.name[0]

	img_id = find_id(glob.CONFIG["image"], img_name, "name")
	if img_id == -1:
		eprint("unable to find image "+img_name)

	dev = find(glob.CONFIG["device"], glob.CONFIG["image"][img_id]["name"], "image")
	if dev is not None:
		eprint("device "+dev["node"]+" uses image "+img_name)

	del glob.CONFIG["image"][img_id]

	set_conf(glob.CONFIG)


def image_show(options):
	conf = glob.CONFIG
	print_object_array(conf["image"], ["name", "user", "pass"])


def image_help():
	markdown_help("image")
