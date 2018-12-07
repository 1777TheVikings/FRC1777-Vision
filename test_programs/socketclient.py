import socket

""" This file runs a simple client that connects to the SocketServer
	Component running on the same device. It outputs all data
	packets received. On Linux, netcat can be used instead (nc
	localhost 5810).
"""


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("connecting to localhost:5810...")
sock.connect(('localhost', 5810))
print("connected")

try:
	data_received = b''
	while True:
		data = sock.recv(16)
		data_received += data
		if data_received.endswith(b"\n"):
			print("Angle: " + str(data_received))
		data_received = b''
except Exception as e:
	print(e)
	raise e
finally:
	print("disconnecting")
	sock.send(b"shutdown")
	sock.close()

