import simplejson as json
import struct

def write_message(sock, msg) :
	json_m = json.dumps(msg)
	bts = len(json_m)
	msg = struct.pack('!H', bts) + json_m
	rem = len(msg)
	while rem > 0 :
		sent = sock.send(msg)
		msg = msg[sent:]
		rem -= sent

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
	return json.loads(read_bytes(sock, bts))
