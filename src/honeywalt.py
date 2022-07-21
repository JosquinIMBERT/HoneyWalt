import argparse

from commands.door import honeywalt_door
from commands.controller import honeywalt_controller
from commands.device import honeywalt_device
from commands.image import honeywalt_image
from commands.state import *
import glob
from utils import *


def honeywalt_help():
	markdown_help("honeywalt")


def main():
	glob.init()
	
	##############
	#   GLOBAL   #
	##############
	parser = argparse.ArgumentParser(description='Manage HoneyWalt: a scalable, manageable and realistic honeypot')
	subparsers = parser.add_subparsers(dest="cmd", required=True)

	door_subparser= subparsers.add_parser("door", help="Manage the doors (public servers)")
	ctrl_subparser= subparsers.add_parser("controller", help="Manage the controller (control and monitor traffic)")
	dev_subparser = subparsers.add_parser("device", help="Manage the devices (exposed machines)")
	img_subparser = subparsers.add_parser("image", help="Manage the images (used on the devices)")
	start_subparser= subparsers.add_parser("start", help="Start HoneyWalt")
	commit_subparser= subparsers.add_parser("commit", help="Commit changes on the devices")
	stop_subparser= subparsers.add_parser("stop", help="Stop HoneyWalt")
	restart_subparser= subparsers.add_parser("restart", help="Restart HoneyWalt")
	status_subparser= subparsers.add_parser("status", help="HoneyWalt status")
	help_subparser= subparsers.add_parser("help", help="Print help")


	#############
	#   DOORS   #
	#############
	door_subparsers= door_subparser.add_subparsers(dest="door_cmd", required=True)
	
	# Add a door
	door_add_sp = door_subparsers.add_parser("add", help="Add a door")
	door_add_sp.add_argument("ip", nargs=1, help="Public IP address")
	door_add_sp.add_argument("dev", nargs=1, help="Backend device")
	
	# Change a door
	door_chg_sp = door_subparsers.add_parser("change", help="Change a door information")
	door_chg_sp.add_argument('ip', nargs=1, help='Select with the IP addess')
	door_chg_sp.add_argument("-i", "--ip-address", nargs=1, help="New IP address")
	door_chg_sp.add_argument("-d", "--device", nargs=1, help="New device name")

	# Delete a door
	door_del_sp = door_subparsers.add_parser("del", help="Delete a door")
	door_del_sp.add_argument('ip', nargs=1, help='Select with the IP addess')
	
	# Door show
	door_show_sp= door_subparsers.add_parser("show", help="Show doors")

	# Door help
	door_help_sp= door_subparsers.add_parser("help", help="Print help")
	

	##############
	# CONTROLLER #
	##############
	ctrl_subparsers= ctrl_subparser.add_subparsers(dest="ctrl_cmd", required=True)
	
	# Set controller options
	ctrl_set_sp = ctrl_subparsers.add_parser("set", help="Set controller parameters")
	ctrl_set_sp.add_argument("-d", "--debit", nargs=1, help="Define honeypot's outgoing traffic debit")
	ctrl_set_sp.add_argument("-l", "--latency", nargs=1, help="Define honeypot's outgoing traffic latency")
	
	# Controller show
	ctrl_show_sp= ctrl_subparsers.add_parser("show", help="Show controller")

	# Controller help
	ctrl_help_sp= ctrl_subparsers.add_parser("help", help="Print help")


	##############
	#   DEVICE   #
	##############
	dev_subparsers= dev_subparser.add_subparsers(dest="dev_cmd", required=True)
	
	# Add device
	dev_add_sp = dev_subparsers.add_parser("add", help="Add a backend device")
	dev_add_sp.add_argument("name", nargs=1, help="Name")
	dev_add_sp.add_argument("mac_addr", nargs=1, help="MAC address")
	dev_add_sp.add_argument("image", nargs=1, help="Walt image")

	# Change device
	dev_chg_sp = dev_subparsers.add_parser("change", help="Change a backend device information")
	dev_chg_sp.add_argument("name", nargs=1, help="Name")
	dev_chg_sp.add_argument("-n", "--name", nargs=1, help="New device name", dest='new_name')
	dev_chg_sp.add_argument("-i", "--image", nargs=1, help="New image")
	
	# Device show
	dev_show_sp= dev_subparsers.add_parser("show", help="Show devices")

	# Device help
	dev_help_sp= dev_subparsers.add_parser("help", help="Print help")


	#############
	#   IMAGE   #
	#############
	img_subparsers= img_subparser.add_subparsers(dest="img_cmd", required=True)

	# Add image
	img_add_sp = img_subparsers.add_parser("add", help="Add an image")
	img_add_sp.add_argument("name", nargs=1, help="Name")
	img_add_sp.add_argument("-u", "--user", nargs=1, help="Username")
	img_add_sp.add_argument("-p", "--password", nargs=1, help="Password")

	# Change image
	img_chg_sp = img_subparsers.add_parser("change", help="Change an image information")
	img_chg_sp.add_argument("name", nargs=1, help="Name")
	img_chg_sp.add_argument("-u", "--user", nargs=1, help="New username")
	img_chg_sp.add_argument("-p", "--password", nargs=1, help="New password")
	
	# Image show
	img_show_sp= img_subparsers.add_parser("show", help="Show images")

	# Image help
	img_help_sp= img_subparsers.add_parser("help", help="Print help")


	#############
	#  CONTROL  #
	#############
	commit_subparser.add_argument("-n", "--no-regen", action="store_true", help="Do not \
		re-generate the configuration files for Cowrie and Wireguard.")


	#############
	#   START   #
	#############
	options = parser.parse_args()
	if options.cmd == "door":
		honeywalt_door(options)
	elif options.cmd == "controller":
		honeywalt_controller(options)
	elif options.cmd == "device":
		honeywalt_device(options)
	elif options.cmd == "image":
		honeywalt_image(options)
	elif options.cmd == "start":
		honeywalt_start(options)
	elif options.cmd == "commit":
		honeywalt_commit(options)
	elif options.cmd == "stop":
		honeywalt_stop(options)
	elif options.cmd == "restart":
		honeywalt_restart(options)
	elif options.cmd == "status":
		honeywalt_status(options)
	else:
		honeywalt_help()

if __name__ == '__main__':
	main()