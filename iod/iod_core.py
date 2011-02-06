import struct
import simplejson as json

import SocketServer

from com.neuronrobotics.sdk.dyio import DyIO
from com.neuronrobotics.sdk.dyio.peripherals import DigitalInputChannel
from com.neuronrobotics.sdk.serial import SerialConnection

class IODHandler(SocketServer.BaseRequestHandler) :
	def handle(self) :
		self.data = self.request.recv(10)
		print 'got req: %s' % self.data
		self.request.send('hi')

class IOD(SocketServer.TCPServer) :
	def __init__(self, serial, port) :
		self.serial = serial
		self.port = port
		self.dyio = DyIO(SerialConnection(self.serial))
		self.dyio.connect()
		self.channels = [None] * 24
		SocketServer.TCPServer.__init__(self, ('0.0.0.0', self.port), IODHandler)

	def shutdown(self) :
		self.dyio.removeAllDyIOEventListeners()
		self.dyio.stopHeartBeat()
		self.dyio.disconnect()

	def setupChannel(self, n, t=DigitalInputChannel) :
		self.channels[n] = t(dyio.getChannel(n))
