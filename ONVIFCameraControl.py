import zeep
from onvif import ONVIFCamera, ONVIFService


# monkey patch
def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

from datetime import timedelta
from vector3 import vector3

import logging

logger = logging.getLogger(__name__)


class ONVIFCameraControl:
    def __init__(self, addr, login, pwd, wsdl_path):
        if not isinstance(addr, tuple) or not isinstance(addr[0], str) or not isinstance(addr[1], int):
            raise TypeError(f'addr must be of type tuple(str, int)')

        logger.info(f'Initializing camera {addr}')

        self.cam = ONVIFCamera(addr[0], addr[1], login, pwd, wsdl_path)
        self.media = self.cam.create_media_service()
        self.ptz = self.cam.create_ptz_service()
        self.profile = self.media.GetProfiles()[0]
        self.request = {k: self.ptz.create_type(k) for k in
                        ['ContinuousMove', 'GotoHomePosition',
                         'AbsoluteMove', 'RelativeMove']}
        for _, r in self.request.items():
            r.ProfileToken = self.profile.token
        self.stop()
        self.config = self.__get_configurations()
        self.status = self.ptz.GetStatus({'ProfileToken': self.profile.token})
        self.node = self.__get_node(self.config.NodeToken)

        self.request['ContinuousMove'].Velocity = self.status.Position
        for _, r in self.request.items():
            r.ProfileToken = self.profile.token

        logging.info(f'Initialized camera at {addr} successfully')

    def __get_ptz_conf_opts(self):
        logger.debug(f'Getting configuration options')
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.profile.PTZConfiguration.token
        return self.ptz.GetConfigurationOptions(request)

    def __get_configurations(self):
        logger.debug(f'Getting configurations')
        request = self.ptz.create_type('GetConfigurations')
        return self.ptz.GetConfigurations(request)[0]

    def __get_node(self, node_token):
        logger.debug(f'Getting node {node_token}')
        request = self.ptz.create_type('GetNode')
        request.NodeToken = node_token
        return self.ptz.GetNode(request)

    def set_preset(self, preset_token=None, preset_name=None):
        logger.info(f'Setting preset {preset_token} ({preset_name})')
        request = self.ptz.create_type('SetPreset')
        request.ProfileToken = self.profile.token
        request.PresetToken = preset_token
        request.PresetName = preset_name
        return self.ptz.SetPreset(request)

    def goto_preset(self, preset_token, ptzs=vector3(1.0, 1.0, 1.0)):
        logger.info(f'Moving to preset {preset_token}, speed={ptzs}')
        request = self.ptz.create_type('GotoPreset')
        request.ProfileToken = self.profile.token
        request.PresetToken = preset_token
        request.Speed = self.status.Position
        vel = request.Speed
        vel.PanTilt.x, vel.PanTilt.y = ptzs.x, ptzs.y
        vel.Zoom.x = ptzs.z
        return self.ptz.GotoPreset(request)

    def get_presets(self):
        logger.debug(f'Getting presets')
        return self.ptz.GetPresets(self.profile.token)

    def move_continuous(self, ptz, timeout=None):
        logger.info(f'Continuous move {ptz} {"" if timeout is None else " for " + str(timeout)}')
        req = self.request['ContinuousMove']
        vel = req.Velocity
        vel.PanTilt.x, vel.PanTilt.y, vel.Zoom.x = ptz.x, ptz.y, ptz.z
        # force default space
        vel.PanTilt.space, vel.Zoom.space = None, None
        if timeout is not None:
            if type(timeout) is timedelta:
                req.Timeout = timeout
            else:
                raise TypeError('timeout parameter is of datetime.timedelta type')
        self.ptz.ContinuousMove(req)

    def move_absolute(self, ptz, ptzs=vector3(1.0, 1.0, 1.0)):
        logger.info(f'Absolute move {ptz}')
        req = self.request['AbsoluteMove']
        pos = req.Position
        pos.PanTilt.x, pos.PanTilt.y = ptz.x, ptz.y
        pos.Zoom.x = ptz.z
        vel = req.Speed
        vel.PanTilt.x, vel.PanTilt.y = ptzs.x, ptzs.y
        vel.Zoom.x = ptzs.z
        self.ptz.AbsoluteMove(req)

    def move_relative(self, ptz, ptzs=vector3(1.0, 1.0, 1.0)):
        logger.info(f'Relative move {ptz}')
        req = self.request['RelativeMove']
        pos = req.Translation
        pos.PanTilt.x, pos.PanTilt.y = ptz.x, ptz.y
        pos.Zoom.x = ptz.z
        vel = req.Speed
        vel.PanTilt.x, vel.PanTilt.y = ptzs.x, ptzs.y
        vel.Zoom.x = ptzs.z
        self.ptz.RelativeMove(req)

    def go_home(self):
        logger.info(f'Moving home')
        self.ptz.GotoHomePosition(self.request['GotoHomePosition'])

    def stop(self):
        logger.info(f'Stopping')
        self.ptz.Stop({'ProfileToken': self.request['ContinuousMove'].ProfileToken})
