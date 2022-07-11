import re, sys

from config import get_conf, set_conf
from utils import eprint, markdown_help, to_root_path


def honeywalt_controller(options):
	if options.ctrl_cmd == "set":
		controller_set(options)
	else:
		controller_help()


def match_value(val, unit):
	regex = re.compile("\A\d+(\.\d*)?"+str(unit)+"\Z")
	return regex.match(val) is not None


def controller_set(options):
	debit = None if options.debit is None else options.debit[0]
	latency = None if options.latency is None else options.latency[0]

	if debit is None and latency is None:
		eprint("controller set: error: no new value was given")

	conf = get_conf()

	if debit is not None:
		rate_unit = "[kmgt]?(bps|bit)"
		if match_value(debit, rate_unit):
			conf["controller"]["debit"] = debit
		else:
			eprint("controller set: error: invalid debit.\nRun \"honeywalt controller set help\" to see format")

	if latency is not None:
		time_unit = "[mu]?(s|sec|secs)"
		if match_value(latency, time_unit):
			conf["controller"]["latency"] = latency
		else:
			eprint("controller set: error: invalid latency.\nRun \"honeywalt controller set help\" to see format")

	set_conf(conf)

def controller_help():
	markdown_help("controller")