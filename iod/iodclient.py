import socket
import iod_proto

class IODClient :
	def __init__(self, ip, port) :
		self.ip = ip
		self.port = port
		self.sock = None
	
	def connect(self) :
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.ip, self.port)) # TODO handle connection failure
		return sock

	def call(self, msg, response=False) :
		sock = self.connect()
		try :
			iod_proto.write_message(sock, msg)
			return iod_proto.unwrap_message(iod_proto.read_message(sock), response=response)
		finally :
			sock.close()
	
	def reset(self) :
		return self.call({iod_proto.SLOT_OP : iod_proto.OP_RESET})

	def setup(self, channelmap) :
		return self.call({iod_proto.SLOT_OP : iod_proto.OP_SETUP, iod_proto.SLOT_ARG : channelmap})

	def sample(self, channels) :
		return self.call({iod_proto.SLOT_OP : iod_proto.OP_SAMPLE, iod_proto.SLOT_ARG : channels}, response=True)

	def set(self, channelmap) :
		return self.call({iod_proto.SLOT_OP : iod_proto.OP_SET, iod_proto.SLOT_ARG : channelmap})
