import sys
from os.path import abspath, dirname, join

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

# get the path to a file in the application
def to_root_path(path):
	root_path = get_root_path()
	return join(root_path, path)