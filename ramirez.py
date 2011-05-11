#!/usr/bin/env python

import getopt
import sys
import os.path
import ConfigParser

import mcore.events
import mcore.sensor
import iod.iod_proto as proto

SENSORS_DIR = 'sensors'

class Ramirez(object) :
	def __init__(self, config, pretend=False, run=False) :
		self.config = config
		self.run = run
		self.pretend = pretend

		self.sensors = []
		self.dyios = {}

		self.processor = mcore.events.Processor()
		self.data_dir = os.path.join(os.path.expanduser("~"), '.ramirez', 'data')
		self.readConfiguration()
		self.actOnConfiguration()

	def readConfiguration(self) :
		self.configuration = ConfigParser.ConfigParser()
		self.configuration.read(self.config)

	def actOnConfiguration(self) :
		section_list = self.configuration.sections()
		section_list.sort() # this is important: sensors will be after sensors.  FIXME needs to change later when
		# alphabetical order is no longer very useful for this.
		for name in section_list :
			names = name.split('.')
			if names[0] == 'storage' :
				try :
					data_dir = self.configuration.get(name, 'dir')
				except :
					raise RuntimeError("Config section storage must include a dir option.")

				if not os.path.isdir(data_dir) :
					raise RuntimeError("storage.dir = %s is not a directory." % data_dir)

				self.data_dir = data_dir
			elif names[0] == 'dyio' :
				dyio_name = names[1]
				ip = self.configuration.get(name, 'ip')
				port = int(self.configuration.get(name, 'port'))
				self.dyios[dyio_name] = mcore.sensor.DyIO(dyio_name, ip, port)
			elif names[0] == 'sensor' :
				sensor_name = names[1]
				typ = self.configuration.get(name, 'type')
				period = int(self.configuration.get(name, 'period'))
				sopts = {
					'tms' : period,
					'tems' : 5000,
					'se' : 0,
				}
				if typ not in mcore.sensor.types :
					raise RuntimeError("Unknown sensor type=%s for sensor %s" % (typ, name))

				if typ == 'boolean-shell' :
					source = self.configuration.get(name, 'source')
					self.sensors.append(mcore.sensor.types[typ](name, self, sopts, script=os.path.join(SENSORS_DIR, source)))
				elif typ == 'boolean-dyio' :
					dyio = self.dyios[self.configuration.get(name, 'dyio')] # TODO handle error
					channel = int(self.configuration.get(name, 'channel'))
					self.sensors.append(mcore.sensor.types[typ](name, self, sopts, dyio, channel))
				else :
					pass # TODO error
			else :
				raise RuntimeError("Unknown config section %s." % name)
		for dyio in self.dyios.values() :
			dyio.hardware_setup()
	
	def sampleAll(self) :
		for sensor in self.sensors :
			t, v = sensor.sample()
			print "sensor %s reported %s in %2.1f seconds" % (sensor.name, v, t)
			
	def runForever(self) :
		print 'starting the run system'
		while True :
			print 'running event cycle'
			self.processor.do()

	def go(self) :
		if self.run :
			self.runForever()
		else :
			self.sampleAll()

def parse(args) :
	optlist, args = getopt.getopt(args, 'c:r', ["pretend"])

	if args :
		raise RuntimeError("No args, they were: %s" % args)

	config = None
	run = False
	pretend = False

	for opt, arg in optlist :
		if opt == '--pretend' :
			pretend = True
		if opt == '-c' :
			config = arg
		if opt == '-r' :
			run = True

	return Ramirez(config=config, pretend=pretend, run=run)

if __name__ == '__main__' :
	ramirez = parse(sys.argv[1:])
	ramirez.go()
