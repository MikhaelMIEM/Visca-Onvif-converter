import socket
import binascii as ba
import ONVIFCameraControl as occ

SERVER_IP = 'localhost'
SERVER_PORT = 12345
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_SOCKET.bind((SERVER_IP, SERVER_PORT))

CAM_IP = ''
CAM_PORT = 80
CAM_LOGIN = 'admin'
CAM_PASSWORD = 'Supervisor'

def recv(sock, bufsize=16): 
	data, addr = sock.recvfrom(bufsize)
	text = ba.b2a_hex(data).decode().upper()
	print('recv "{}" from {}'.format(' '.join([text[i:i+2] for i in range(0, len(text), 2)]), addr))
	return data, addr

def send(sock, data, addr):
	sock.sendto(ba.unhexlify(data.replace(' ', '')), addr)
	print('sent "{}" to {}'.format(data, addr))


def command_type(command):
	if command[0:2]=='\x81\x09':
		return 'inquiry'
	else:
		return 'control'

def inquiry(command, socket, addr):
	if command==b'\x81\x09\x06\x12\xff':
		response='90 50 00 00 00 01 00 00 00 01 FF' #pan tilt pos
	elif command==b'\x81\x09\x04\x47\xFF':
		response='90 50 01 01 01 01 FF' #zoom pos
	elif command==b'\x81\x09\x04\x48\xFF':
		response='90 50 01 01 01 01 FF' #focus pos
	else:
		response='90 41 FF'
		
	send(socket, response, addr)
	
def control(command, cam):
	if command==b'\81x\01x\06x\01x\0Cx\0Ax\01x\03x\FF':
		cam.move_left()
	if command==b'\81x\01x\06x\01x\0Cx\0Ax\02x\03x\FF':
		cam.move_right()

while True:
	data, addr = recv(SERVER_SOCKET)
	
	if command_type(data)=='inquiry':
		inquiry(data, SERVER_SOCKET, addr)
	