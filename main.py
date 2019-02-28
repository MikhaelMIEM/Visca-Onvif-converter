from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
from datetime import timedelta
from os import path
from server import Server
import json
import threading
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-20s) %(message)s',
)

from time import sleep

with open('cameras.conf', 'r') as f:
    config = json.load(f)

servers = [Server(c['IP'], c['PORT'], c['VISCA_PORT'], c['LOGIN'], c['PASSWORD']) for c in config['CAMERAS']]

threads = []
for s in servers:
    t = threading.Thread(target=s.run)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

#cam = OCC('192.168.15.43', 80, 'admin', 'Supervisor',
#          path.join(path.dirname(__file__), 'wsdl'))

#cam.move_continuous(vector3(0, 0, -0.1), timedelta(seconds=4))
#cam.go_home()
