import os, socket, sys, threading

import glob
from utils import *

# TODO: check how to use untrusted/unsafe strings
#		(when checking the values returned by the
#		VM)

class ControlSocket:
	def __init__(self, phase):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.socket.connect()
		self.socket.bind((glob.CONTROL_IP, glob.CONTROL_PORT))
		self.phase = phase

	def initiate(self, backends=[], usernames=[], passwords=[], images=[]):
		self.socket.listen(1)
		self.conn_sock, self.conn_addr = self.socket.accept()
		self.sock = self.conn_sock.makefile(mode="rw")

		if not self.wait_confirm():
			eprint("ControlSocket.initiate: error: VM failed to boot")
		self.sock.write(str(phase))
		if self.phase == 1:
			self.send_elems(images)
			if self.wait("done"):
				# Sending the users to be added to the images
				# This will allow cowrie to connect (and will
				# allow brut force from a node to another)
				self.send_elems(usernames)
				self.send_elems(passwords)
				self.send_elems(backends)
			else:
				eprint("ControlSocket.initiate: error: failed to download WalT images on the VM")
			return self.recv_elems() # Returning backends IPs
		return None

	def ask_reboot(self, backend):
		self.sock.write("reboot:"+backend)
		return self.wait_confirm()

	def wait(self, expected_result, timeout=30):
		ready, _, _ = select.select([self.sock], [], [], timeout)
		if len(ready)>0:
			res = self.sock.readline()
			return res == expected_result
		else:
			return None

	def wait_confirm(self, timeout=30):
		ready, _, _ = select.select([self.conn_sock], [], [], timeout)
		if len(ready)>0:
			return self.conn_sock.recv(1) == b"1"
		return False

	def send_elems(self, elems):
		str_elems = ""
		for elem in elems:
			str_elems += str(elem)
		self.sock.write(str_elems)

	def recv_elems(self, sep=" "):
		elems = self.sock.readline()
		return elems.split(sep)

	def close(self):
		self.conn_sock.close()
		self.socket.close()