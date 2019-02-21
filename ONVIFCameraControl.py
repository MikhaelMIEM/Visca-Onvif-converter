import zeep
from onvif import ONVIFCamera, ONVIFService

# monkey patch
def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue

zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

from time import sleep
from vector3 import vector3


class ONVIFCameraControl:
    def __init__(self, addr, port, login, pwd, wsdl_path):
        print("Initializing camera", addr)
        self.cam = ONVIFCamera(addr, port, login, pwd, wsdl_path)
        self.media = self.cam.create_media_service()
        self.ptz = self.cam.create_ptz_service()
        self.profile = self.media.GetProfiles()[0]
        self.request = {k: self.ptz.create_type(k) for k in
                        ['ContinuousMove', 'GotoHomePosition',
                         'AbsoluteMove', 'RelativeMove']}
        for _, r in self.request.items():
            r.ProfileToken = self.profile.token
        self.request['ContinuousMove'].Velocity = self.ptz.GetStatus({'ProfileToken': self.profile.token}).Position
        self.stop()
        self.config = self.__get_ptz_conf_opts()
        for _, r in self.request.items():
            r.ProfileToken = self.profile.token
        print('Initialization complete')

    def __get_ptz_conf_opts(self):
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.profile.PTZConfiguration.token
        return self.ptz.GetConfigurationOptions(request)

    def move_continuous(self, ptz, timeout=None):
        print('Continuous move',ptz,'for',str(timeout)+'s')
        req = self.request['ContinuousMove']
        vel = req.Velocity
        vel.PanTilt.x, vel.PanTilt.y = ptz.x, ptz.y
        vel.Zoom.x = ptz.z
        self.ptz.ContinuousMove(req)
        if timeout is not None:
            sleep(timeout)
            self.stop()

    def move_absolute(self, ptz, ptzs=vector3(1.0, 1.0, 1.0)):
        print('Absolute move',ptz)
        req = self.request['AbsoluteMove']
        pos = req.Position
        pos.PanTilt.x, pos.PanTilt.y = ptz.x, ptz.y
        pos.Zoom.x = ptz.z
        vel = req.Speed
        vel.PanTilt.x, vel.PanTilt.y = ptzs.x, ptzs.y
        vel.Zoom.x = ptzs.z
        self.ptz.AbsoluteMove(req)

    def move_relative(self, ptz, ptzs=vector3(1.0, 1.0, 1.0)):
        print('Relative move',ptz)
        req = self.request['RelativeMove']
        pos = req.Translation
        pos.PanTilt.x, pos.PanTilt.y = ptz.x, ptz.y
        pos.Zoom.x = ptz.z
        vel = req.Speed
        vel.PanTilt.x, vel.PanTilt.y = ptzs.x, ptzs.y
        vel.Zoom.x = ptzs.z
        self.ptz.RelativeMove(req)

    def go_home(self):
        print('Moving home')
        self.ptz.GotoHomePosition(self.request['GotoHomePosition'])

    def stop(self):
        self.ptz.Stop({'ProfileToken': self.request['ContinuousMove'].ProfileToken})
