import socket
import threading
import os
import sys

from utils import *

# TODO: check how to use untrusted/unsafe strings
#		(when checking the values returned by the
#		VM)

ADDR = "127.0.0.1"
PORT = 5555

class ControlSocket:
	def __init__(self, phase):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect()
		self.sock = self.socket.makefile(mode="rw")
		self.phase = phase

	def initiate(self, backends=[], usernames=[], passwords=[], images=[]):
		if not self.wait("boot"): # TODO add a timer
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
		return self.wait("done")

	def wait(self, expected_result):
		res = self.sock.readline() # TODO add a timer
		return res == expected_result

	def send_elems(self, elems):
		str_elems = ""
		for elem in elems:
			str_elems += str(elem)
		self.sock.write(str_elems)

	def recv_elems(self, sep=" "):
		elems = self.sock.readline()
		return elems.split(sep)

	def close(self):
		self.sock.close()
		if self.socket is not None:
			self.socket.close()