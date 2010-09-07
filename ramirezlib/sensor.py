import os
import os.path
import time

"""
This module is for base classes useful for acquiring sensor data of boolean or numeric value.
It does not cover specific sensor types or any history recording or history lookup functionality.
"""

class Sensor(object) :
	def __init__(self, name) :
		self.name = name

class BooleanSensor(Sensor) :
	def __init__(self, name, script) :
		if not os.path.exists(script) :
			raise RuntimeError("script %s does not exist." % script)
		if not os.access(script, os.X_OK) :
			raise RuntimeError("script %s is not executable." % script)

		Sensor.__init__(self, name)

		self.script = script
	
	def sample(self) :
		begin = time.time()
		pid = os.fork()
		if pid == 0 :
			os.execvp(self.script, [self.script])
		else :
			pid, status = os.waitpid(pid, 0)
			status = status / 256
			return time.time() - begin, status == 0

types = {
	'boolean' : BooleanSensor
}
