import os, select, socket, sys, threading

import glob
from utils import *

# TODO: check how to use untrusted/unsafe strings
#		(when checking the values returned by the
#		VM)

class ControlSocket:
	def __init__(self, phase):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((glob.CONTROL_IP, glob.CONTROL_PORT))
		self.sock = self.socket.makefile(mode="rw")
		self.phase = phase

	def initiate(self, backends=[], usernames=[], passwords=[], images=[]):
		print("Waiting boot.")
		if not self.wait_confirm(timeout=90):
			eprint("ControlSocket.initiate: error: VM failed to boot")
		
		print("Send phase.")
		self.send(str(self.phase))
		
		if self.phase == 1:
			print("Send images.")
			self.send_elems(images)
			print("Wait confirm.")
			if self.wait_confirm():
				# Sending the users to be added to the images
				# This will allow cowrie to connect (and will
				# allow brut force from a node to another)
				print("Send usernames.")
				self.send_elems(usernames)
				print("Send passwords.")
				self.send_elems(passwords)
				print("Send backends.")
				self.send_elems(backends)
			else:
				eprint("ControlSocket.initiate: error: failed to download WalT images on the VM")
			print("Receive IPs.")
			return self.recv_elems() # Returning backends IPs
		return None

	def ask_reboot(self, backend):
		self.send("reboot:"+backend)
		return self.wait_confirm()

	def wait_confirm(self, timeout=30):
		res = self.recv(max_iter=timeout)
		return res[0] == "1"

	def send(self, string):
		self.sock.write(string+"\n")

	def recv(self, max_iter=30):
		res = ""
		i = 0
		while True and i<max_iter:
			i+=1
			res = self.sock.readline()
			if not res:
				time.sleep(1)
				continue
			break
		if i >= max_iter:
			eprint("ControlSocket:recv: error: reached max_iter")
		return res

	def send_elems(self, elems, sep=" "):
		str_elems = ""
		for elem in elems:
			str_elems += str(elem) + sep
		self.send(str_elems)

	def recv_elems(self, sep=" "):
		elems = self.recv()
		if elems.strip()=="":
			return []
		return elems.split(sep)

	def close(self):
		self.socket.close()


def main():
    socket = ControlSocket(1)
    socket.initiate(backends=[], usernames=[], passwords=[], images=[])

if __name__ == '__main__':
        main()