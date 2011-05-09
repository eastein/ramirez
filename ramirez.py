#!/usr/bin/env python

import getopt
import sys
import os.path
import ConfigParser

import mcore.sensor

SENSORS_DIR = 'sensors'

class Ramirez(object) :
	def __init__(self, config, pretend=False) :
		self.config = config
		self.pretend = pretend
		self.sensors = []
		self.readConfiguration()
		self.actOnConfiguration()
		self.data_dir = os.path.join(os.path.expanduser("~"), '.ramirez', 'data')

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
				if typ not in mcore.sensor.types :
					raise RuntimeError("Unknown sensor type=%s for sensor %s" % (typ, name))
				self.sensors.append(mcore.sensor.types[typ](name=name, script=os.path.join(SENSORS_DIR, source)))
			else :
				raise RuntimeError("Unknown config section %s." % name)
	
	def sampleAll(self) :
		for sensor in self.sensors :
			t, v = sensor.sample()
			print "sensor %s reported %s in %2.1f seconds" % (sensor.name, v, t)
			

def parse(args) :
	optlist, args = getopt.getopt(args, 'c:', ["pretend"])

	if args :
		raise RuntimeError("No args, they were: %s" % args)

	config = None
	pretend = False

	for opt, arg in optlist :
		if opt == '--pretend' :
			pretend = True
		if opt == '-c' :
			config = arg

	return Ramirez(config=config, pretend=pretend)

if __name__ == '__main__' :
	ramirez = parse(sys.argv[1:])
	ramirez.sampleAll()
