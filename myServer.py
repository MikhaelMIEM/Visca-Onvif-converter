import socket
import binascii as ba
from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
from os import path

addr = None #udalit' potom

SERVER_IP = 'localhost'
SERVER_PORT = 12345
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_SOCKET.bind((SERVER_IP, SERVER_PORT))

CAM_IP = '192.168.15.43'
CAM_PORT = 80
CAM_LOGIN = 'admin'
CAM_PASSWORD = 'Supervisor'

CAM = OCC(CAM_IP, CAM_PORT, CAM_LOGIN, CAM_PASSWORD,
          path.join(path.dirname(__file__), 'wsdl'))

def byte_and(a, b):
	return bytes(i & j for i, j in zip(a, b))
	
def byte_not(a):
	bytes(i ^ 0xFF for i in a)


def recv(sock, bufsize=16): 
	data, addr = sock.recvfrom(bufsize)
	text = ba.b2a_hex(data).decode().upper()
	print('recv "{}" from {}'.format(' '.join([text[i:i+2] for i in range(0, len(text), 2)]), addr))
	return data, addr

def send(sock, data, addr):
	sock.sendto(ba.unhexlify(data.replace(' ', '')), addr)
	print('sent "{}" to {}'.format(data, addr))


def handle_inquiry(command):
	if command==b'\x06\x12':
		response='90 50 00 00 00 01 00 00 00 01 FF' #pan tilt pos
	elif command==b'\x04\x47':
		response='90 50 01 01 01 01 FF' #zoom pos
	elif command==b'\x04\x48':
		response='90 50 01 01 01 01 FF' #focus pos
	else:
		response='90 61 41 FF' #error
	
	global SERVER_SOCKET
	global addr
	send(SERVER_SOCKET, response, addr)
	

def handle_pan_tilt_drive(byts):
	if byts[-1]==3 and byts[-2]==3:
		CAM.stop()
		return

	if byts[-2]==3: pan=0
	else:
		pan=byts[0]/24
		if byts[-2]==1: pan=-pan
		
	if byts[-1]==3: tilt=0
	else:
		tilt=byts[0]/20
		if byts[-1]==2: tilt=-tilt

	CAM.move_continuous(vector3(pan, tilt, 0))
	
PREFIX = {
	b'\x81\x01\x06\x01': handle_pan_tilt_drive,
	b'\x81\x09': handle_inquiry
}
	
def command_processing(command):
	global PREFIX
	for p in PREFIX:
		if command[:len(p)]==p:
			PREFIX[p](command[len(p):-1])

while True:
	data, addr = recv(SERVER_SOCKET)
	
	command_processing(data)
		
		
	