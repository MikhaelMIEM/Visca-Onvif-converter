from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
from os import path

cam = OCC(('192.168.15.55', 8999), 'admin', 'Supervisor',
          path.join(path.dirname(__file__), 'wsdl'))

p = cam.get_presets()
cam.goto_preset(2, vector3(0.1, 0.1, 0.1))

