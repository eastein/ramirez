#!/usr/bin/env python
import socket
import struct
import pprint
import iod_proto
import time
import sys

def request(msg) :
	tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp_sock.connect(('127.0.0.1', 7823))
	iod_proto.write_message(tcp_sock, msg)
	print '>>> request'
	pprint.pprint(iod_proto.read_message(tcp_sock))
	print '<<< response'
	tcp_sock.close()

if __name__ == '__main__' :
	request({iod_proto.SLOT_OP : iod_proto.OP_RESET})

	if sys.argv[1] == 'in' :
		request({iod_proto.SLOT_OP : iod_proto.OP_SETUP, iod_proto.SLOT_ARG : [[0, iod_proto.CHANNELTYPE_DIGITAL], [23, iod_proto.CHANNELTYPE_DIGITAL]]})
		while True :
			request({iod_proto.SLOT_OP : iod_proto.OP_SAMPLE, iod_proto.SLOT_ARG : [0, 23]})
			time.sleep(1)
	elif sys.argv[1] == 'out' :
		request({iod_proto.SLOT_OP : iod_proto.OP_SETUP, iod_proto.SLOT_ARG : [[23, iod_proto.CHANNELTYPE_DIGITALOUT]]})

		val = False
		while True :
			val = not val
			request({iod_proto.SLOT_OP : iod_proto.OP_SET, iod_proto.SLOT_ARG : [[23, val]]})
			time.sleep(2)
	elif sys.argv[1] == 'buzz' :
		request({iod_proto.SLOT_OP : iod_proto.OP_SETUP, iod_proto.SLOT_ARG : [[23, iod_proto.CHANNELTYPE_DIGITALOUT]]})
		request({iod_proto.SLOT_OP : iod_proto.OP_SET, iod_proto.SLOT_ARG : [[23, False]]})

		def set_lock_pin(v) :
			request({iod_proto.SLOT_OP : iod_proto.OP_SET, iod_proto.SLOT_ARG : [[23, v]]})

		while True :
			line = sys.stdin.readline().split("\n")[0]
			if line == 'buzz' :
				print 'unlocking door'
				set_lock_pin(True)
				time.sleep(1)
				set_lock_pin(False)
			else :
				print 'unknown command %s' % line
