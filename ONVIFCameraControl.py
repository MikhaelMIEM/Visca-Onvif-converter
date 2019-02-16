from onvif import ONVIFCamera
import os.path

class ONVIFCameraControl:

	def __init__(self, ip, port, login, password):
		
		print '---initializing',ip,port
		self.mycam = ONVIFCamera(ip, port, login, password)
		print 'creating media service'
		self.media = self.mycam.create_media_service()
		self.ptz = self.mycam.create_ptz_service()
		
		self.media_profile = self.media.GetProfiles()[0]
		
		print 'creating requests'
		request = self.ptz.create_type('GetConfigurationOptions')
		request.ConfigurationToken = self.media_profile.PTZConfiguration._token
		ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

		self.moverequest = self.ptz.create_type('ContinuousMove')
		self.moverequest.ProfileToken = self.media_profile._token

		print 'stopping ptz'
		self.ptz.Stop({'ProfileToken': self.media_profile._token})
		self.active = False #camera status

		print 'ass'
		self.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
		print(self.XMAX)
		self.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
		self.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
		self.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
		print '---initialized',ip,port
		
	def __do_move(self, request):
		if self.active:
			self.ptz.Stop({'ProfileToken': self.moverequest.ProfileToken})
		self.active=True
		self.ptz.ContinuousMove(request)
		
			
	def move_left(self):
		self.moverequest.Velocity.PanTilt.x = self.XMIN
		self.moverequest.Velocity.PanTilt.y = 0
		self.__do_move()
		
	def move_right(self):
		self.moverequest.Velocity.PanTilt.x = self.XMAX
		self.moverequest.Velocity.PanTilt.y = 0
		self.__do_move(self.moverequest)
	
	def stop(self):
		self.ptz.Stop({'ProfileToken': self.media_profile._token})
		self.active = False