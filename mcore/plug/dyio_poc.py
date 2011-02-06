#!/usr/bin/env jython

import sys, time

sys.path.append('/home/eastein/nr-sdk/nrsdk-0.3.7.a-jar-with-dependencies.jar')

from com.neuronrobotics.sdk.dyio import DyIO
from com.neuronrobotics.sdk.dyio.peripherals import DigitalInputChannel
from com.neuronrobotics.sdk.serial import SerialConnection

if __name__ == '__main__' :
	dyio = DyIO(SerialConnection("/dev/ttyACM0"))
	dyio.connect()
	dig = DigitalInputChannel(dyio.getChannel(0))

	while True :
		print dig.isHigh()
		time.sleep(.25)
