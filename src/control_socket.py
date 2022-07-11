import socket
import threading
import os
import sys

from utils import eprint

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

	def initiate(self, ports=[], backends=[], usernames=[], passwords=[], images=[]):
		if not self.wait_boot():
			eprint("ControlSocket.initiate: error: VM failed to boot")
		self.sock.write(str(phase))
		if self.phase == 1:
			if self.wait_images_downloaded():
				# Sending the users to be added to the images
				# This will allow cowrie to connect (and will
				# allow brut force from a node to another)
				self.send_elems(images)
				self.send_elems(usernames)
				self.send_elems(passwords)
			else:
				eprint("ControlSocket.initiate: error: failed to download WalT images on the VM")
			return None
		else:
			# The VM should know to which ports wireguard
			# should send its traffic (and the corresponding
			# backends)
			self.send_elems(ports)
			self.send_elems(backends)
			ips = self.recv_elems()
			return ips

	def ask_reboot(self, backend):
		self.sock.write("reboot:"+backend)
		reboot_res = self.sock.readline()
		return reboot_res == "done"

	def wait_boot(self):
		boot_res = self.sock.readline()
		return boot_res == "boot"

	def wait_images_downloaded():
		download_res = self.sock.readline()
		return download_res == "done"

	def send_elems(self, elems):
		str_elems = ""
		for elem in elems:
			str_elems += str(elem)
		self.sock.write(str_elems)

	def recv_elems(self):
		elems = self.sock.readline()
		return elems.split(" ")

	def close(self):
		self.sock.close()
		if self.socket is not None:
			self.socket.close()