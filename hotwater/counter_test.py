#!/usr/bin/env python

from serial import Serial
from DS2423 import DS2423

linkusb = Serial(
	port = '/dev/ttyUSB0',
	baudrate = 9600,
	timeout = 0.1)

d = DS2423('Counter', '880000000F1A981D')

print d.readCounterA(linkusb)

linkusb.close()
