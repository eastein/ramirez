import os
import os.path
import time
import random
import events
import trace

"""
This module is for classes useful for acquiring sensor data of boolean or numeric value.
It does not cover specific sensor types or any history recording or history lookup functionality.

That functionality is provided by the mcore.trace module.
"""

class Sensor(events.Processable) :
	def __init__(self, name, ramirez, sampleopts) :
		self.name = name
		self.period = sampleopts['tms']
		tems = sampleopts['tems']
		se = sampleopts['se']
		self.trace = trace.Trace(name, os.path.join(ramirez.data_dir, '%s.db' % name), self.period, tems, se)
		events.Processable.__init__(self, processor=ramirez.processor)
		self.schedule()

	def schedule(self, tick=None) :
		if not tick :
			tick = events.tick()
		self.processor.add(events.SampleEvent(tick, self))

	def sample(self) :
		print 'calling core sample'
		start = events.tick()
		value = self.perform_sample()
		duration = max(0, events.tick() - start)
		print 'duration was %d ms' % duration
		measure = self.trace.write(value).result()
		nextcall = max(0, measure.when_ms + self.period - duration)
		print 'running next at %d' % nextcall
		self.schedule(nextcall)

class BooleanSensor(Sensor) :
	pass

class BooleanShellSensor(Sensor) :
	def __init__(self, name, ramirez, sampleopts, script) :
		if not os.path.exists(script) :
			raise RuntimeError("script %s does not exist." % script)
		if not os.access(script, os.X_OK) :
			raise RuntimeError("script %s is not executable." % script)

		Sensor.__init__(self, name, ramirez, sampleopts)

		self.script = script
	
	def perform_sample(self) :
		pid = os.fork()
		if pid == 0 :
			os.execvp(self.script, [self.script])
		else :
			pid, status = os.waitpid(pid, 0)
			status = status / 256
			return status == 0

types = {
	'boolean-shell' : BooleanShellSensor
}
