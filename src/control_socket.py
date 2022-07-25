import os, select, socket, sys, threading

import glob
from utils import *

# TODO: check how to use untrusted/unsafe strings
#		(when checking the values returned by the
#		VM)

def to_bytes(string):
	b = bytearray()
	b.extend(string.encode())
	return b

def to_string(bytes):
	return bytes.decode('ascii')

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
			self.conn, addr = self.socket.accept()
		except socket.timeout:
			eprint("ControlSocket.initiate: error: it seems like the VM failed to boot.")
		except:
			eprint("ControlSocket.initiate: error: unknown error occured when waiting for the VM")
		else:
			print("Send phase.")
			self.send(str(self.phase))
			self.wait_confirm()
			
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
					self.wait_confirm()
					print("Send passwords.")
					self.send_elems(passwords)
					self.wait_confirm()
					print("Send backends.")
					self.send_elems(backends)
					self.wait_confirm()
				else:
					eprint("ControlSocket.initiate: error: failed to download WalT images on the VM")
				print("Receive IPs.")
				ips = self.recv_elems()
				self.send_confirm() 
				return ips
			return None

	def send_confirm(self):
		self.send("1")

	def send_fail(self):
		self.send("0")

	def ask_reboot(self, backend):
		self.send("reboot:"+backend)
		return self.wait_confirm()

	def wait_confirm(self, timeout=30):
		res = self.recv(timeout=timeout)
		return res[0] == "1"

	def send(self, string):
		self.conn.send(to_bytes(string+"\n"))

	def recv(self, timeout=30):
		self.conn.settimeout(timeout)
		try:
			res = self.conn.recv(2048)
		except socket.timeout:
			eprint("ControlSocket.recv: error: reached timeout")
		except:
			eprint("ControlSocket.recv: error: an unknown error occured")
		else:
			return to_string(res)

	def send_elems(self, elems, sep=" "):
		str_elems = ""
		for elem in elems:
			str_elems += str(elem) + sep
		self.send("["+str_elems+"]")

	def recv_elems(self, sep=" "):
		elems = str(self.recv()).strip()
		elems = elems[1:len(elems)-1].strip()
		if not elems:
			return []
		return elems.split(sep)

	def close(self):
		if conn is not None:
			self.conn.close()
		self.socket.close()


def main():
    socket = ControlSocket(1)
    socket.initiate(backends=[], usernames=[], passwords=[], images=[])

if __name__ == '__main__':
        main()