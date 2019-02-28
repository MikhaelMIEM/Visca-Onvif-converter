from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
from os import path

cam = OCC('192.168.15.43', 80, 'admin', 'Supervisor',
          path.join(path.dirname(__file__), 'wsdl'))

cam.move_continuous(vector3(0, 1, 1), 2)
cam.go_home()
