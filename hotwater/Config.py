"""
 collects the configuration information from the specific
 configuration file
"""

import sys
import ConfigParser

class Config():
	def __init__(self, configFile):

		self.configFile = configFile
	
		try:
			self.config = ConfigParser.ConfigParser()
			self.config.read(self.configFile)

		except:
			print "Could not load %s" % (self.configFile)
			exceptionType, exceptionValue = sys.exc_info()[:2]
			print "Type:", exceptionType
			print "Value:", exceptionValue
			raise Exception
	
	def get(self, sectionName = None, parameter = None):
		try:
			if sectionName != None and parameter != None:
				return self.config.get(sectionName, parameter)
			else:
				return None

		except:
			exceptionType, exceptionValue = sys.exc_info()[:2]
			print "Type:", exceptionType
			print "Value:", exceptionValue
			raise Exception
