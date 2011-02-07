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

		msg = {iod_proto.SLOT_STATUS : iod_proto.STATUS_FAIL}
		try :
			if request[iod_proto.SLOT_OP] == iod_proto.OP_RESET :
				msg = self.server.op_reset()
			elif request[iod_proto.SLOT_OP] == iod_proto.OP_SETUP :
				msg = self.server.op_setup(request[iod_proto.SLOT_ARG])
			elif request[iod_proto.SLOT_OP] == iod_proto.OP_SAMPLE :
				msg = self.server.op_sample(request[iod_proto.SLOT_ARG])
			else :
				print 'unk op: %d' % request[iod_proto.SLOT_OP]
		except :
			print 'caught exception in handler'
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

			return {iod_proto.SLOT_STATUS : iod_proto.STATUS_OK}
		finally :
			self.dyio_lock.release()

	def op_setup(self, arg) :
		self.dyio_lock.acquire()
		try :
			if self.setup is not False :
				# TODO define code to include error type codes, apply it to all instances of STATUS_FAIL
				return {iod_proto.SLOT_STATUS : iod_proto.STATUS_FAIL}

			setup = set()
			for channel, channeltype in arg :
				if channel in setup :
					return {iod_proto.SLOT_STATUS : iod_proto.STATUS_FAIL}
				# TODO do not ignore channeltype
				self.channels[channel] = DigitalInputChannel(self.dyio.getChannel(channel))
			self.setup = True

			return {iod_proto.SLOT_STATUS : iod_proto.STATUS_OK}
		finally :
			self.dyio_lock.release()

	def op_sample(self, arg) :
		self.dyio_lock.acquire()
		try :
			if not self.setup :
				return {iod_proto.SLOT_STATUS : iod_proto.STATUS_FAIL}
			for channelid in arg :
				# TODO keyerror handle
				if self.channels[channelid] is None :
					return {iod_proto.SLOT_STATUS : iod_proto.STATUS_FAIL}

			samples = []
			for channelid in arg :
				# TODO time of sample collection in the packet?
				samples.append((channelid, self.channels[channelid].isHigh()))

			return {iod_proto.SLOT_STATUS : iod_proto.STATUS_OK, iod_proto.SLOT_DATA : samples}
		finally :
			self.dyio_lock.release()
