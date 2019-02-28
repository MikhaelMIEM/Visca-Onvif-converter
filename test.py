from ONVIFCameraControl import ONVIFCameraControl as OCC
from vector3 import vector3
from datetime import timedelta
from os import path
import json
import asyncio

# with open('cameras.conf', 'r') as f:
#     config = json.load(f)
#
# tasks = []
# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()

cam = OCC('192.168.15.43', 80, 'admin', 'Supervisor',
          path.join(path.dirname(__file__), 'wsdl'))

cam.move_continuous(vector3(0, 0, -0.1), timedelta(seconds=4))
cam.go_home()
