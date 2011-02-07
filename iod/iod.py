#!/usr/bin/env jython

import os.path
import sys, time
import getopt

if __name__ == '__main__' :
	opts, args = getopt.getopt(sys.argv[1:], "", ["port=", "nrsdk=", "serial=", "libpath="])
	
	serial = "/dev/ttyACM0"
	port = 7823
	nrsdk = None
	libpath = None
	
	for o, a in opts :
		if o == '--nrsdk' :
			nrsdk = a
		elif o == '--port' :
			port = int(a)
		elif o == '--serial' :
			serial = a
		elif o == '--libpath' :
			libpath = a

	if nrsdk is None :
		print 'You must give --nrsdk=[jar path]'
		sys.exit(1)

	if not os.path.exists(serial) :
		print 'Serial device %s does not exist.' % serial

	sys.path.append(nrsdk)
	for p in libpath.split(':') :
		sys.path.append(p)

	import iod_core
	iod = iod_core.IOD(serial, port)
	iod.serve_forever()
	# TODO enable a way to cleanly shut down, on SIGTERM probably. that's what people do.
	#iod.shutdown_dyio()
	# shut down the tcpserver somehow too
