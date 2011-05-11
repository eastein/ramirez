import threading
import socket
import iod_proto as prot

class IODClient :
	def __init__(self, ip, port) :
		self.ip = ip
		self.port = port
		self.sock = None
		self.initialized = False
		self.lock = threading.Lock()
		self.lock.acquire()

	def connect(self) :
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.ip, self.port)) # TODO handle connection failure
		return sock

	def call(self, msg, response=False) :
		sock = self.connect()
		try :
			prot.write_message(sock, msg)
			return prot.unwrap_message(prot.read_message(sock), response=response)
		finally :
			sock.close()
	
	def reset(self) :
		return self.call({prot.SLOT_OP : prot.OP_RESET})

	def setup(self, channelmap) :
		if self.initialized :
			self.lock.acquire()
		try :
			return self.call({prot.SLOT_OP : prot.OP_SETUP, prot.SLOT_ARG : channelmap})
		finally :
			self.lock.release()

	def sample(self, channels) :
		self.lock.acquire()
		try :
			return self.call({prot.SLOT_OP : prot.OP_SAMPLE, prot.SLOT_ARG : channels}, response=True)
		finally :
			self.lock.release()

	def set(self, channelmap) :
		self.lock.acquire()
		try :
			return self.call({prot.SLOT_OP : prot.OP_SET, prot.SLOT_ARG : channelmap})
		finally :
			self.lock.release()
