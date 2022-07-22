import os, sys, subprocess
from os.path import abspath, dirname, exists, join

# TO BE TESTED: kill_from_file

# Print an error and exit
def eprint(*args, exit=True, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    if exit:
    	sys.exit(1)

# Print a warning
def wprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Find an object in the "objects" list with field "field" equal "target"
def find(objects, target, field):
	for obj in objects:
		if obj[field] == target:
			return obj
	return None

# Find the id of an object in the "objects" list with field "field" equal "target"
def find_id(objects, target, field):
	i=0
	for obj in objects:
		if obj[field] == target:
			return i
		i += 1
	return -1

# Get the path to the root of the application
def get_root_path():
	path = abspath(dirname(__file__))
	return "/".join(path.split("/")[:-1])

# Kill a process using the file "filename"
# Several methods can be used:
#	filetype=pid	=> read the pid in the file
#	filetype=ssh	=> the file is an ssh control socket
def kill_from_file(filename, filetype="pid"):
	if filetype=="pid":
		with open(filename, "r+") as pidfile:
			pid = pidfile.read()
			pidfile.seek(0)
			pidfile.truncate()
			if pid != "":
				pid = int(pid)
				os.kill(pid, signal.SIGTERM)
	elif filetype=="ssh":
		kill_cmd = "ssh -S "+filename+" -O exit 0.0.0.0"
		res = subprocess.run(kill_cmd, shell=True ,check=True, text=True)
		if res.returncode != 0:
			eprint("utils.kill_from_file: error: ssh exit command returned non-zero code")
	else:
		eprint("utils.kill_from_file: error: unknown file type")

# Print the markdown help page from the documentation directory
def markdown_help(name):
	with open(to_root_path("doc/"+name+".md")) as file:
		print(file.read())

def print_object_array(objects, fields):
	max_length = {}
	for field in fields:
		max_length[field] = len(field)

	for obj in objects:
		for field in fields:
			txt = obj.get(field) or ""
			length = len(txt)
			if length > max_length[field]:
				max_length[field] = length

	break_size = 3
	line = ""
	separator = ""
	for field in fields:
		line += field + " " * (max_length[field] - len(field) + break_size)
		separator += "-" * max_length[field] + " " * break_size
	print(line)
	print(separator)
	for obj in objects:
		line = ""
		for field in fields:
			txt = obj.get(field) or ""
			line += txt + " " * (max_length[field] - len(txt) + break_size)
		print(line)


def run(command, error, output=False):
	res = subprocess.run(command, shell=True ,check=True, text=True, capture_output=output)
	if res.returncode != 0:
		eprint(error)
	if output:
		return str(res.stdout)
	else:
		return None


def door_run(door, cmd, err="", output=False):
	ssh_temp = Template("ssh root@${ip} -i {keypath} -p {port} \"${command}\"")

	ssh_cmd = ssh_temp.substitute({
		"ip": door["host"],
		"keypath": glob.DOOR_PRIV_KEY,
		"port": door["realssh"],
		"command": cmd
	})

	return run(ssh_cmd, error=err, output=output)


def vm_run(cmd, err="", output=False):
	ssh_temp = Template("ssh root@${ip} -i {keypath} -p {port} \"${command}\"")

	ssh_cmd = ssh_temp.substitute({
		"ip": glob.VM_IP,
		"keypath": glob.VM_PRIV_KEY,
		"port": 22,
		"command": cmd
	})

	return run(ssh_cmd, error=err, output=output)


# get the path to a file in the application
def to_root_path(path):
	root_path = get_root_path()
	return join(root_path, path)

def is_pid(file):
	if exists(file):
		with open(file, "r") as pidfile:
			pid = pidfile.read()
			if pid != "":
				return str(int(pid))
	return None


def delete(directory, suffix=""):
	for name in os.listdir(directory):
		file = os.path.join(directory,name)
		if file.endswith(suffix):
			os.remove(file)