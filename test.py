from ONVIFCameraControl1 import ONVIFCameraControl
from time import sleep


cams = [ONVIFCameraControl('192.168.15.43', 80, 'admin', 'Supervisor'),]

for c in cams:
	print('testing movement')

	c.move_up()