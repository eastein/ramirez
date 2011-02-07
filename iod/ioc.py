#!/usr/bin/env python
import socket
import struct
import pprint
import iod_proto

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
	request({iod_proto.SLOT_OP : iod_proto.OP_SETUP, iod_proto.SLOT_ARG : [[0, iod_proto.CHANNELTYPE_DIGITAL]]})
