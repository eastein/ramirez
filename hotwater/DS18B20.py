"""
	interact with a DS18B20 temperature sensor
"""

import time
import pdb

class DS18B20 ():
	
	def __init__(self, name, serial):
		self.serial	= serial
		self.name	= name

		self.address = ''
		for index in range(len(self.serial) - 1, -1, -2):
			self.address = self.address + self.serial[index -1] + self.serial[index]
		return

	def convert(self, bus):
		bus.write('r')
		bus.read(3)
		bus.write('b' + '55' + self.address + '44' + '\r')
		self.temperatureReadyAt = time.time() + 0.9
		bus.read(2 + len(self.address) + 2 + 2)

		return

	def retrieveTemp(self, bus):
		timeToWait = self.temperatureReadyAt - time.time()

		if timeToWait > 0:
			time.sleep(timeToWait)

		bus.write('r')
		bus.read(3)

		bus.write('b' + '55' + self.address + 'BE')
		bus.read(2 + len(self.address) + 2 + 2)

		temperature = 0.0
		tempHexDigits = []

		bus.write('FF')
		tempHexDigits.append(bus.read(2))
		bus.write('FF')
		tempHexDigits.append(bus.read(2))
		bus.write('\r')
		bus.read(4)

		tempHexString = tempHexDigits[1] + tempHexDigits[0]
		try:
			temperature = float.fromhex(tempHexString) / 16.0

		except:
			temperature = 0.0
			
		return temperature

