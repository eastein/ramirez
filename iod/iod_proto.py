import simplejson as json
import struct

SLOT_OP = 0
SLOT_STATUS = 1
SLOT_ARG = 2
SLOT_DATA = 3

OP_RESET = 0
OP_SETUP = 1
OP_SAMPLE = 2
OP_SET = 3

STATUS_OK = 0
STATUS_FAIL = 1

CHANNELTYPE_DIGITAL = 0
CHANNELTYPE_ANALOG = 1
CHANNELTYPE_DIGITALOUT = 2

def write_message(sock, msg) :
	json_m = json.dumps(msg)
	bts = len(json_m)
	msg = struct.pack('!H', bts) + json_m
	rem = len(msg)
	while rem > 0 :
		sent = sock.send(msg)
		msg = msg[sent:]
		rem -= sent

# TODO fix spin on failure to read or silent connection drop, wastes cpu
def read_bytes(sock, b) :
	rem = b
	bytes = ''
	while rem > 0 :
		r = sock.recv(rem)
		bytes += r
		rem -= len(r)
	return bytes

def read_message(sock) :
	bts, = struct.unpack('!H', read_bytes(sock, 2))
	preproc_message = json.loads(read_bytes(sock, bts))
	message = {}
	for k in preproc_message.keys() :
		message[int(k)] = preproc_message[k]
	return message
