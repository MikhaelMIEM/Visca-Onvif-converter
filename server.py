import logging

logger = logging.getLogger(__name__)

from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
import common

import socket
import binascii as ba

from os import path


class Server:

    def __init__(self, server_addr, cam_addr, login, password, client_num=1):
        common.check_addr(server_addr)
        common.check_addr(cam_addr)
        logger.info(f'Initializing service {server_addr} -> {cam_addr}')

        self.PREFIX = {
            b'\x81\x01\x06\x01': self.handle_pan_tilt_drive,
            b'\x81\x09': self.handle_inquiry,
            b'\x81\x01\x06\x04': self.handle_home,
            b'\x81\x01\x04\x07': self.handle_zoom,
            b'\x81\x01\x06\x02': self.handle_absolute_position
        }
        
        self.clients = {}
        self.client_num = client_num
		
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(server_addr)


        self.cam = OCC(cam_addr, login, password,
                       path.join(path.dirname(__file__), 'wsdl'))

        self.last_addr = None
		
    def client_inquiry_processing(self):
        if self.last_addr not in self.clients:
            if len(self.clients) <= self.client_num:
                self.clients[self.last_addr]= self.cam.node['MaximumNumberOfPresets']//self.client_num*len(list(self.clients))+1
            else:
                return b'\x90\x61\x41\xFF'
        else:
            if self.clients[self.last_addr]+1 == self.cam.node['MaximumNumberOfPresets']//self.client_num*(list(self.clients).index(self.last_addr)+1):
                self.clients[self.last_addr] = self.cam.node['MaximumNumberOfPresets']//self.client_num*list(self.clients).index(self.last_addr)+1
            else:
                self.clients[self.last_addr] += 1
        self.cam.set_preset(self.clients[self.last_addr])
        return b''.join([b'\x90\x50\x00\x00\x00\x00\x00\x00',
                        bytes([self.clients[self.last_addr] // 16, self.clients[self.last_addr] % 16]),
                        b'\xFF'])
            

    def recieve(self, bufsize=16):
        data, addr = self.server_socket.recvfrom(bufsize)
        logger.debug(f'Received {data.hex()} from {addr}')
        return data, addr

    def send(self, sock, data, addr):
        logger.debug(f'Sending {data.hex()}')
        sock.sendto(data, addr)

    def handle_inquiry(self, command):
        logger.debug(f'Handling inquiry {command.hex()}')
        if command == b'\x06\x12':
            response = self.client_inquiry_processing()
        elif command == b'\x04\x47':
            response = b'\x90\x50\x01\x01\x01\x01\xFF'  # zoom position
        elif command == b'\x04\x48':
            response = b'\x90\x50\x01\x01\x01\x01\xFF'  # focus position
        else:
            response = b'\x90\x61\x41\xFF'  # error

        self.send(self.server_socket, response, self.last_addr)

    def handle_pan_tilt_drive(self, arg):
        logger.debug(f'Handling pan tilt drive {arg.hex()}')
        if arg[-1] == 3 and arg[-2] == 3:
            self.cam.stop()
            return

        if arg[-2] == 3:
            pan = 0
        else:
            pan = arg[0] / 24
            if arg[-2] == 1: pan = -pan

        if arg[-1] == 3:
            tilt = 0
        else:
            tilt = arg[0] / 20
            if arg[-1] == 2: tilt = -tilt

        self.cam.move_continuous(vector3(pan, tilt, 0))

    def handle_home(self, arg):
        logger.debug(f'Handling goto home')
        self.cam.go_home()

    def handle_zoom(self, arg):
        if arg == 0:
            self.cam.stop()
            return

        zoom = arg[0] % 16 / 7
        if arg[0] // 16 == 3: zoom = -zoom

        self.cam.move_continuous(vector3(0, 0, zoom))

    def handle_absolute_position(self, arg):
        logger.debug(f'Handling absolute move (as goto preset) {arg.hex()}')
        self.cam.goto_preset((arg[-2] << 8) | arg[-1])

    def command_processing(self, command):
        for p in self.PREFIX:
            if command[:len(p)] == p:
                self.PREFIX[p](command[len(p):-1])

    def run(self):
        try:
            while True:
                data, self.last_addr = self.recieve()
                self.command_processing(data)
        except (KeyboardInterrupt, SystemExit):
            logger.info(f'Processing loop interrupted')
