from __future__ import print_function

from onvif import ONVIFCamera
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

        self.request['ContinuousMove'].Velocity = self.profile.PTZConfiguration.DefaultPTZSpeed

        self.stop()

        self.config = self.__get_ptz_conf_opts()
        contVelSpace = self.config.Spaces.ContinuousPanTiltVelocitySpace[0]
        contZoomSpace = self.config.Spaces.ContinuousZoomVelocitySpace[0]
        absPosSpace = self.config.Spaces.AbsolutePanTiltPositionSpace[0]
        absZoomSpace = self.config.Spaces.AbsoluteZoomPositionSpace[0]
        self.range = {
            'PanVelMax': contVelSpace.XRange.Max,
            'PanVelMin': contVelSpace.XRange.Min,
            'TiltVelMax': contVelSpace.YRange.Max,
            'TiltVelMin': contVelSpace.YRange.Min,
            'ZoomVelMax': contZoomSpace.XRange.Max,
            'ZoomVelMin': contZoomSpace.XRange.Min,
            'PanPosMax': absPosSpace.XRange.Max,
            'PanPosMin': absPosSpace.XRange.Min,
            'TiltPosMax': absPosSpace.YRange.Max,
            'TiltPosMin': absPosSpace.YRange.Min,
            'ZoomPosMax': absZoomSpace.XRange.Max,
            'ZoomPosMin': absZoomSpace.XRange.Min
        }

        for _, r in self.request.items():
            r.ProfileToken = self.profile._token

    def __get_ptz_conf_opts(self):
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.profile.PTZConfiguration._token
        return self.ptz.GetConfigurationOptions(request)

    def move_continuous(self, ptz, timeout=1):
        print('Continuous move',ptz,'for',str(timeout)+'s')
        req = self.request['ContinuousMove']
        vel = req.Velocity
        vel.PanTilt._x, vel.PanTilt._y = ptz.x, ptz.y
        vel.Zoom._x = ptz.z
        self.ptz.ContinuousMove(req)
        sleep(timeout)
        self.stop()

    def move_absolute(self, ptz, ptzs=vector3(1.0, 1.0, 1.0)):
        print('Absolute move',ptz)
        req = self.request['AbsoluteMove']
        pos = req.Position
        pos.PanTilt._x, pos.PanTilt._y = ptz.x, ptz.y
        pos.Zoom._x = ptz.z
        vel = req.Speed
        vel.PanTilt._x, vel.PanTilt._y = ptzs.x, ptzs.y
        vel.Zoom._x = ptzs.z
        self.ptz.AbsoluteMove(req)

    def move_relative(self, ptz, ptzs=vector3(1.0, 1.0, 1.0)):
        print('Relative move',ptz)
        req = self.request['RelativeMove']
        pos = req.Translation
        pos.PanTilt._x, pos.PanTilt._y = ptz.x, ptz.y
        pos.Zoom._x = ptz.z
        vel = req.Speed
        vel.PanTilt._x, vel.PanTilt._y = ptzs.x, ptzs.y
        vel.Zoom._x = ptzs.z
        self.ptz.RelativeMove(req)

    def go_home(self):
        print('Moving home')
        self.ptz.GotoHomePosition(self.request['GotoHomePosition'])

    def stop(self):
        self.ptz.Stop({'ProfileToken': self.profile._token})
