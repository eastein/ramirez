#!/usr/bin/env python

import getopt
import sys
import os.path
import ConfigParser

import mcore.events
import mcore.sensor

SENSORS_DIR = 'sensors'

class Ramirez(object) :
	def __init__(self, config, pretend=False, run=False) :
		self.config = config
		self.run = run
		self.pretend = pretend
		self.sensors = []
		self.processor = mcore.events.Processor()
		self.data_dir = os.path.join(os.path.expanduser("~"), '.ramirez', 'data')
		self.readConfiguration()
		self.actOnConfiguration()

	def readConfiguration(self) :
		self.configuration = ConfigParser.ConfigParser()
		self.configuration.read(self.config)

	def actOnConfiguration(self) :
		for name in self.configuration.sections() :
			names = name.split('.')
			if names[0] == 'storage' :
				try :
					data_dir = self.configuration.get(name, 'dir')
				except :
					raise RuntimeError("Config section storage must include a dir option.")

				if not os.path.isdir(data_dir) :
					raise RuntimeError("storage.dir = %s is not a directory." % data_dir)

				self.data_dir = data_dir
			elif names[0] == 'sensor' :
				sensor_name = names[1]
				typ = self.configuration.get(name, 'type')
				source = self.configuration.get(name, 'source')
				period = int(self.configuration.get(name, 'period'))
				sopts = {
					'tms' : period,
					'tems' : 5000,
					'se' : 0
				}
				if typ not in mcore.sensor.types :
					raise RuntimeError("Unknown sensor type=%s for sensor %s" % (typ, name))
				self.sensors.append(mcore.sensor.types[typ](name, self, sopts, script=os.path.join(SENSORS_DIR, source)))
			else :
				raise RuntimeError("Unknown config section %s." % name)
	
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
