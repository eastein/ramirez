#!/usr/bin/env python
import socket
import struct
import pprint
import iod_proto
import time
import sys
import tty
import iodclient

if __name__ == '__main__' :
	client = iodclient.IODClient('127.0.0.1', 7823)
	client.reset()

	if sys.argv[1] == 'in' :
		client.setup([[0, iod_proto.CHANNELTYPE_DIGITAL], [1, iod_proto.CHANNELTYPE_DIGITAL]])

		while True :
			print client.sample([0, 1])
			time.sleep(1)
	elif sys.argv[1] == 'out' :
		client.setup([[23, iod_proto.CHANNELTYPE_DIGITALOUT]])

		val = False
		while True :
			val = not val
			client.set([[23, val]])
			time.sleep(2)
	elif sys.argv[1] == 'buzz' :
		tty.setraw(sys.stdin.fileno())

		client.setup([[23, iod_proto.CHANNELTYPE_DIGITALOUT]])
		client.set([[23, False]])

		def set_lock_pin(v) :
			client.set([[23, v]])

		while True :
			c = sys.stdin.read(1)
			if c in ['b', '\t'] :
				print 'unlocking door'
				set_lock_pin(True)
				time.sleep(1)
				set_lock_pin(False)
			elif c == 'q' :
				print 'quit'
				sys.exit(0)
			else :
				print 'unknown command %s' % c
