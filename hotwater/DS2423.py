"""
	interact with a DS2423 counter
"""

import time
import pdb

matchROMCommand = '55'
readMemoryAndCounter = 'A5'
memoryAddress = 'C001'

class DS2423 ():
	
	def __init__(self, name, serial):
		self.serial	= serial
		self.name	= name

		self.address = ''
		for index in range(len(self.serial) - 1, -1, -2):
			self.address = self.address + self.serial[index -1] + self.serial[index]

		print "Address = ", self.address

		return

	def readCounterA(self, bus):
		#
		# reset the bus
		#
		bus.write('r')
		print bus.read(4)

		#
		# enter "byte" mode
		#
		bus.write('b')

		#
		# address the device
		#
		bus.write(matchROMCommand + self.address)
		print bus.read(len(matchROMCommand) + len(self.address))

		#
		# issue "read memory and counter" command
		#
		bus.write(readMemoryAndCounter)
		bus.write(memoryAddress)
		print bus.read(len(readMemoryAndCounter) + len(memoryAddress))


		#
		# read 32 bytes of data
		#
		for dataIndex in range(0, 32, 1):
			bus.write('FF')
			print bus.read(2)

		#
		# then read the counter bytes
		#
		counterHexDigits = []
		for counterIndex in range(0, 4, 1):
			bus.write('FF')
			counterHexDigits.append(bus.read(2))

		#
		# leave "byte" mode
		#
		bus.write('\r')
		bus.read(4)

		counterHexString = counterHexDigits[3] + counterHexDigits[2] + counterHexDigits[1] + counterHexDigits[0]
		try:
			counter = int(counterHexString, 16)
			print "Counter in hex: ", counterHexString
			print "Counter in decimal: ", counter

		except:
			counter = 0
			
		return counter

