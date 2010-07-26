#!/usr/bin/env python

import getopt
import sys
import os.path
import ConfigParser

import sqlalchemy

from ramirezlib import sensor

SENSORS_DIR = 'sensors'

class Ramirez(object) :
	def __init__(self, config, pretend=False) :
		self.config = config
		self.pretend = pretend
		self.sensors = []

	def readConfiguration(self) :
		self.configuration = ConfigParser.ConfigParser()
		self.configuration.read(self.config)

	def doEverything(self) :
		self.readConfiguration()
		for name in self.configuration.sections() :
			obj = self.configuration.get(name, 'object')
			if obj == 'sensor' :
				typ = self.configuration.get(name, 'type')
				source = self.configuration.get(name, 'source')
				if typ not in sensor.types :
					raise RuntimeError("Unknown sensor type=%s for sensor %s" % (typ, name))
				self.sensors.append(sensor.types[typ](name=name, script=os.path.join(SENSORS_DIR, source)))
			else :
				raise RuntimeError("Unknown object=%s for %s" % (obj, name))
	
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

	ramirez.doEverything()
	ramirez.sampleAll()
