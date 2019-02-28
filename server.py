import socket
import binascii as ba
from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
from os import path


class Server:

	def __init__(self):
	
		self.PREFIX = {
			b'\x81\x01\x06\x01': self.handle_pan_tilt_drive,
			b'\x81\x09': self.handle_inquiry,
			b'\x81\x01\x06\x04': self.handle_home,
			b'\x81\x01\x04\x07': self.handle_zoom
		}
	
		self.SERVER_IP = 'localhost'
		self.SERVER_PORT = 12345
		self.SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.SERVER_SOCKET.bind((self.SERVER_IP, self.SERVER_PORT))

		CAM_IP = '192.168.15.43'
		CAM_PORT = 80
		CAM_LOGIN = 'admin'
		CAM_PASSWORD = 'Supervisor'

		self.CAM = OCC(CAM_IP, CAM_PORT, CAM_LOGIN, CAM_PASSWORD,
			path.join(path.dirname(__file__), 'wsdl'))
			
		self.last_addr = None


	def recv(self, bufsize=16): 
		data, addr = self.SERVER_SOCKET.recvfrom(bufsize)
		text = ba.b2a_hex(data).decode().upper()
		print('recv "{}" from {}'.format(' '.join([text[i:i+2] for i in range(0, len(text), 2)]), addr))
		return data, addr

	def send(self, sock, data, addr):
		sock.sendto(ba.unhexlify(data.replace(' ', '')), addr)
		print('sent "{}" to {}'.format(data, addr))


	def handle_inquiry(self, command):
		if command==b'\x06\x12':
			response='90 50 00 00 00 01 00 00 00 01 FF' #pan tilt pos
		elif command==b'\x04\x47':
			response='90 50 01 01 01 01 FF' #zoom pos
		elif command==b'\x04\x48':
			response='90 50 01 01 01 01 FF' #focus pos
		else:
			response='90 61 41 FF' #error
		
		self.send(self.SERVER_SOCKET, response, self.last_addr)
		

	def handle_pan_tilt_drive(self, byts):
		if byts[-1]==3 and byts[-2]==3:
			self.CAM.stop()
			return

		if byts[-2]==3: pan=0
		else:
			pan=byts[0]/24
			if byts[-2]==1: pan=-pan
			
		if byts[-1]==3: tilt=0
		else:
			tilt=byts[0]/20
			if byts[-1]==2: tilt=-tilt

		self.CAM.move_continuous(vector3(pan, tilt, 0))
		
	def handle_home(self, byts):
		self.CAM.go_home()
		
	def handle_zoom(self, byts):
		if byts==0:
			self.CAM.stop()
			return
		
		zoom=byts[0]%16/7
		if byts[0]//16==3: zoom=-zoom
		
		self.CAM.move_continuous(vector3(0,0, zoom)) 
	
	def command_processing(self, command):
		for p in self.PREFIX:
			if command[:len(p)]==p:
				self.PREFIX[p](command[len(p):-1])
				
	def run(self):
		while True:
			data, self.last_addr = self.recv()
			self.command_processing(data)
	