import argparse, os, select, socket, sys, threading, time


def encode_len(bytes_obj):
	return len(bytes_obj).to_bytes(2, "big")

def decode_len(length):
	return int.from_bytes(length, "big")


def controller_tunnel(
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
			i=0
			while i<6: # ~30sec
				try:
					tcp_sock.connect((tcp_host, tcp_port))
				except:
					time.sleep(5)
				else:
					break
				i+=1
			if i>=6:
				print("[ERROR] traffic-shaper.controller_tunnel: failed to connect to the door")
				sys.exit(1)

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


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Transform UDP into TCP')
	parser.add_argument("pid_file", nargs=1, help="Path to the PID file")

	parser.add_argument("udp_lo_host", nargs=1, help="UDP host to listen from")
	parser.add_argument("udp_lo_port", nargs=1, help="UDP port to listen to")
	parser.add_argument("tcp_host", nargs=1, help="TCP host to connect to")
	parser.add_argument("tcp_port", nargs=1, help="TCP port to connect to")

	options = parser.parse_args()
	# Write PID
	with open(options.pid_file[0], "w") as pid_file:
		pid_file.write(str(os.getpid()))
	# Run adapter
	controller_tunnel(
		options.udp_lo_host[0],
		int(options.udp_lo_port[0]),
		options.tcp_host[0],
		int(options.tcp_port[0])
	)