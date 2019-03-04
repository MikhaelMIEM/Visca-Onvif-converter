import socket
import binascii as ba
from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
from os import path
import logging


class Server:

	def __init__(self, addr, port, visca_port, login, password):
	
		self.PREFIX = {
			b'\x81\x01\x06\x01': self.handle_pan_tilt_drive,
			b'\x81\x09': self.handle_inquiry,
			b'\x81\x01\x06\x04': self.handle_home,
			b'\x81\x01\x04\x07': self.handle_zoom,
			b'\x81\x01\x06\x02': self.handle_absolute_position
		}

		# TODO: IPv6
		self.SERVER_IP = '0.0.0.0'
		self.SERVER_PORT = visca_port
		self.SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.SERVER_SOCKET.bind((self.SERVER_IP, self.SERVER_PORT))

		self.cam = OCC(addr, port, login, password,
					   path.join(path.dirname(__file__), 'wsdl'))
			
		self.last_addr = None
		self.preset_counter = 0

	def recv(self, bufsize=16):
		data, addr = self.SERVER_SOCKET.recvfrom(bufsize)
		text = ba.b2a_hex(data).decode().upper()
		print('recv "{}" from {}'.format(' '.join([text[i:i+2] for i in range(0, len(text), 2)]), addr))
		return data, addr

	def send(self, sock, data, addr):
		sock.sendto(data, addr)
		text = ba.b2a_hex(data).decode().upper()
		print('send "{}" to {}'.format(' '.join([text[i:i+2] for i in range(0, len(text), 2)]), addr))

	def handle_inquiry(self, command):
		if command==b'\x06\x12':
			response=b''.join([b'\x90\x50\x00\x00\x00\x00\x00\x00',
							   bytes([self.preset_counter//16, self.preset_counter%16]),            #probaply does not work
							   b'\xFF']) #pan tilt position
			if self.preset_counter:
				self.cam.set_preset(self.preset_counter)
				print('Preset seted')                                        #remove zis
			if self.preset_counter>self.cam.node['MaximumNumberOfPresets']:
				self.preset_counter=1
			else:
				self.preset_counter+=1
		elif command==b'\x04\x47':
			response=b'\x90\x50\x01\x01\x01\x01\xFF' #zoom position
		elif command==b'\x04\x48':
			response=b'\x90\x50\x01\x01\x01\x01\xFF' #focus position
		else:
			response=b'\x90\x61\x41\xFF' #error
		
		self.send(self.SERVER_SOCKET, response, self.last_addr)

	def handle_pan_tilt_drive(self, arg):
		if arg[-1]==3 and arg[-2]==3:
			self.cam.stop()
			return

		if arg[-2]==3: pan=0
		else:
			pan= arg[0] / 24
			if arg[-2]==1: pan=-pan
			
		if arg[-1]==3: tilt=0
		else:
			tilt= arg[0] / 20
			if arg[-1]==2: tilt=-tilt

		self.cam.move_continuous(vector3(pan, tilt, 0))
		
	def handle_home(self, arg):
		self.cam.go_home()
		
	def handle_zoom(self, arg):
		if arg==0:
			self.cam.stop()
			return
		
		zoom= arg[0] % 16 / 7
		if arg[0]//16==3: zoom=-zoom
		
		self.cam.move_continuous(vector3(0, 0, zoom))
		
	def handle_absolute_position(self, arg):                                        #probaly doesn't work
		self.cam.goto_preset((arg[-2]<<8)|arg[-1])
	
	def command_processing(self, command):
		for p in self.PREFIX:
			if command[:len(p)]==p:
				self.PREFIX[p](command[len(p):-1])
				
	def run(self):
		while True:
			try:
				data, self.last_addr = self.recv()
				self.command_processing(data)
			except KeyboardInterrupt:
				logging.debug('Terminating loop')
				return
