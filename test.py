from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
from datetime import timedelta
from os import path

cam = OCC('192.168.15.42', 80, 'admin', 'Supervisor',
          path.join(path.dirname(__file__), 'wsdl'))

cam.move_continuous(vector3(0.5, 0.5, 0), timedelta(milliseconds=50))
cam.go_home()
