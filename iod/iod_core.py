import struct
import simplejson as json
import struct
import pprint
import SocketServer

import iod_proto

from com.neuronrobotics.sdk.dyio import DyIO
from com.neuronrobotics.sdk.dyio.peripherals import DigitalInputChannel
from com.neuronrobotics.sdk.serial import SerialConnection

class IODHandler(SocketServer.BaseRequestHandler) :
	def handle(self) :
		request = iod_proto.read_message(self.request)
		print 'got request'
		pprint.pprint(request)
		iod_proto.write_message(self.request, {'status' : 'ok'})

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
