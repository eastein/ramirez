import struct
import simplejson as json
import struct
import pprint
import SocketServer
import threading

import iod_proto

from com.neuronrobotics.sdk.dyio import DyIO
from com.neuronrobotics.sdk.dyio.peripherals import DigitalInputChannel
from com.neuronrobotics.sdk.serial import SerialConnection

class IODHandler(SocketServer.BaseRequestHandler) :
	def handle(self) :
		request = iod_proto.read_message(self.request)
		print 'got request'
		pprint.pprint(request)

		msg = {iod_proto.SLOT_STATUS : iod_proto.STATUS_FAIL}
		try :
			if request[iod_proto.SLOT_OP] == iod_proto.OP_RESET :
				print 'got: reset'
				self.server.op_reset()
				print 'done: reset'
			elif request[iod_proto.SLOT_OP] == iod_proto.OP_SETUP :
				print 'got: setup'
				self.server.op_setup(request[iod_proto.SLOT_ARG])
				print 'done: setup'
			else :
				print 'unk op: %d' % request[iod_proto.SLOT_OP]
		except :
			print 'caught exception in handler'
			raise
		iod_proto.write_message(self.request, msg)

class IOD(SocketServer.TCPServer) :
	def __init__(self, serial, port) :
		self.serial = serial
		self.port = port
		self.dyio_lock = threading.Lock()
		self.startup_dyio()
		SocketServer.TCPServer.__init__(self, ('0.0.0.0', self.port), IODHandler)

	def startup_dyio(self, use_lock=True) :
		if use_lock :
			self.dyio_lock.acquire()
		try :
			self.dyio = DyIO(SerialConnection(self.serial))
			self.dyio.connect()
			self.channels = [None] * 24
			self.setup = False
		finally :
			if use_lock :
				self.dyio_lock.release()

	def shutdown_dyio(self, use_lock=True) :
		if use_lock :
			self.dyio_lock.acquire()
		try :
			self.dyio.removeAllDyIOEventListeners()
			self.dyio.stopHeartBeat()
			self.dyio.disconnect()
		finally :
			if use_lock :
				self.dyio_lock.release()

	def op_reset(self) :
		self.dyio_lock.acquire()
		try :
			try :
				self.shutdown_dyio(use_lock=False)
			except :
				pass
			self.startup_dyio(use_lock=False)
		finally :
			self.dyio_lock.release()

	def op_setup(self, arg) :
		self.dyio_lock.acquire()
		try :
			if self.setup is not False :
				return {iod_proto.SLOT_STATUS : iod_proto.STATUS_FAIL}

			setup = set()
			for channel, channeltype in arg :
				if channel in setup :
					return {iod_proto.SLOT_STATUS : iod_proto.STATUS_FAIL}
				# TODO do not ignore channeltype
				self.channels[channel] = DigitalInputChannel(self.dyio.getChannel(channel))
		finally :
			self.dyio_lock.release()
