#!/usr/bin/env python
import socket
import struct
import pprint
import iod_proto

if __name__ == '__main__' :
	req = {'hi' : 'yo.', 'float' : 4.274, 'int' : 2741}

	tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp_sock.connect(('127.0.0.1', 7823))
	iod_proto.write_message(tcp_sock, req)
	pprint.pprint(iod_proto.read_message(tcp_sock))
	print '^ response'
	tcp_sock.close()
