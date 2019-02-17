from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3

cam = OCC('192.168.15.43', 80, 'admin', 'Supervisor', '/home/akarin/PycharmProjects/vivif/wsdl')
#cam.absoluteMove(-1, -1, 0)
cam.goHome()
cam.continuousMove(vector3(-0.1, -0.1, -0.1), 3)
cam.continuousMove(vector3(0, +0.2, +0.2), 3)
cam.goHome()
