from time import sleep
from onvif import ONVIFCamera

class ONVIFCameraControl:
    def __init__(self, addr, port, login, pwd):
        camera = ONVIFCamera(addr, port, login, pwd)
        self.media_service = camera.create_media_service()
        self.ptz_service = camera.create_ptz_service()
        self.media_profile = self.media_service.GetProfiles()[0]

        ptz_conf_opts = self.__get_ptz_conf_opts()

        self.config = {}
        self.config['VelXMax'] = ptz_conf_opts.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.config['VelXMin'] = ptz_conf_opts.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.config['VelYMax'] = ptz_conf_opts.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.config['VelYMin'] = ptz_conf_opts.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

    def __get_ptz_conf_opts(self):
        request = self.ptz_service.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration._token
        return self.ptz_service.GetConfigurationOptions(request)

    def move_up(self, timeout=1):
        print 'move up...'
        request = self.ptz_service.create_type('ContinuousMove')
        request.ProfileToken = self.media_profile._token
        request.Velocity.PanTilt._x = 0
        request.Velocity.PanTilt._y = self.config['VelYMax']

        self.ptz_service.ContinuousMove(request)
        sleep(timeout)
        self.ptz_service.Stop({'ProfileToken': request.ProfileToken})
