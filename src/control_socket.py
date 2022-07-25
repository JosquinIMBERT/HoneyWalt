import os, select, socket, sys, threading

import glob
from utils import *

# TODO: check how to use untrusted/unsafe strings
#		(when checking the values returned by the
#		VM)

class ControlSocket:
	def __init__(self, phase):
		self.socket = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
		self.socket.bind((socket.VMADDR_CID_HOST, glob.CONTROL_PORT))
		self.socket.settimeout(90) # Timeout for VM connection is 1m30s
		self.socket.listen(1)
		self.phase = phase

	def initiate(self, backends=[], usernames=[], passwords=[], images=[]):
		print("Waiting boot.")

		try:
			conn, addr = self.socket.accept()
		except socket.timeout:
			eprint("ControlSocket.initiate: error: it seems like the VM failed to boot.")
		except:
			eprint("ControlSocket.initiate: error: unknown error occured when waiting for the VM")
		else:
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
		res = self.recv(timeout=timeout)
		return res[0] == "1"

	def send(self, string):
		self.socket.send(string+"\n")

	def recv(self, max_iter=30):
		try:
			res = self.socket.recv(2048)
		except socket.timeout:
			eprint("ControlSocket.recv: error: reached timeout")
		except:
			eprint("ControlSocket.recv: error: an unknown error occured")
		else:
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