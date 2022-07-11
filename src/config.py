import json
from os.path import exists
import sys
from utils import to_root_path

def open_conf(file, write=False):
	if file is None:
		conf_file = to_root_path("etc/honeywalt.cfg")
	else:
		conf_file = file

	if not exists(conf_file) and not write:
		print("The configuration file was not found.")
		sys.exit(1)
	else:
		if write:
			return open(conf_file, "w")
		else:
			return open(conf_file)

def get_conf(file=None):
	conf_file = open_conf(file)
	conf = json.load(conf_file)
	conf_file.close()
	return conf

def set_conf(conf, file=None):
	conf_file = open_conf(file, write=True)
	conf_file.write(json.dumps(conf, indent=4))
	conf_file.close()