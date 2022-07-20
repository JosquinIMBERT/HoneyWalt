import argparse, select, socket, sys, threading


def encode_len(bytes_obj):
	return len(bytes_obj).to_bytes(2, "big")

def decode_len(length):
	return int.from_bytes(length, "big")


def main_controller(
	udp_lo_host="127.0.0.1",
	udp_lo_port=1111,
	tcp_host="192.168.100.1",
	tcp_port=1110):
	udp_host = None
	udp_port = None

	# UDP Server + TCP client
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
		udp_sock.bind((udp_lo_host, udp_lo_port))
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
			tcp_sock.connect((tcp_host, tcp_port))
			sel_list = [udp_sock, tcp_sock]
			try:
				while True:
					rready, _, _ = select.select(sel_list, [], [])
					for ready in rready:
						if ready is udp_sock:
							msg, addr = udp_sock.recvfrom(1024)
							if not msg: break
							udp_host, udp_port = addr
							msg = encode_len(msg) + msg
							tcp_sock.sendall(msg)
						else:
							msg = tcp_sock.recv(1024)
							if not msg: break
							if udp_host is not None and udp_port is not None:
								while msg:
									blen, msg = msg[0:2], msg[2:]
									length = decode_len(blen)
									to_send, msg = msg[:length], msg[length:]
									udp_sock.sendto(to_send, (udp_host, udp_port))
			except ConnectionResetError:
				print("Connection Reset")


def main_door(
	udp_host="127.0.0.1",
	udp_port=51820,
	tcp_host="0.0.0.0",
	tcp_port=1111):
	# TCP Server + UDP client
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_listen:
		tcp_listen.bind((tcp_host, tcp_port))
		tcp_listen.listen(1)
		tcp_sock=None
		try:
			tcp_sock, tcp_addr = tcp_listen.accept()
			with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
				udp_sock.connect((udp_host, udp_port))
				sel_list = [udp_sock, tcp_sock]
				try:
					while True:
						rready, _, _ = select.select(sel_list, [], [])
						for ready in rready:
							if ready is udp_sock:
								msg = udp_sock.recv(1024)
								if not msg: break
								msg = encode_len(msg) + msg
								tcp_sock.sendall(msg)
							else:
								msg = tcp_sock.recv(1024)
								if not msg: break
								while msg:
									blen, msg = msg[0:2], msg[2:]
									length = decode_len(blen)
									to_send, msg = msg[:length], msg[length:]
									udp_sock.sendto(to_send, (udp_host, udp_port))
				except ConnectionResetError:
					print("Connection Reset")
		finally:
			if tcp_sock is not None:
				tcp_sock.close()


if __name__ == '__main__':
	# This program is directly called only on the doors.
	# On the controller, it is called from the app
	parser = argparse.ArgumentParser(description='Transform UDP into TCP')
	parser.add_argument("udp_host", nargs=1, help="IP of the UDP server") # 127.0.0.1
	parser.add_argument("udp_port", nargs=1, help="Port of the UDP server") # 51820
	parser.add_argument("tcp_host", nargs=1, help="IP to listen to") # 0.0.0.0
	parser.add_argument("tcp_port", nargs=1, help="Port to listen to") # 51819

	options = parser.parse_args()
	main_door(
		options.udp_host,
		options.udp_port,
		options.tcp_host,
		options.tcp_port
	)