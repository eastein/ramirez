"""
a generic log setup function
"""

import logging
import logging.handlers

def Log(conf, name):

	logLevels = {
		'DEBUG' : logging.DEBUG,
		'INFO' : logging.INFO,
		'WARNING' : logging.WARNING,
		'ERROR' : logging.ERROR,
		'CRITICAL' : logging.CRITICAL
	}
				
	logger = logging.getLogger(name)
	logger.setLevel(logLevels[conf.get(name, 'logFile.level')])

	formatter = logging.Formatter(
		'%(asctime)s %(name)s %(levelname)s %(message)s'
	)

	sizeInMb = int(conf.get(name, 'logFile.maxMB')) * 1024000
	filename = conf.get(name, 'logFile.path')
	fileHandler = logging.handlers.RotatingFileHandler(
		filename,
		maxBytes = sizeInMb,
		backupCount = int(conf.get(name, 'logFile.archives'))
	)
	fileHandler.setFormatter(formatter)
	logger.addHandler(fileHandler)

	return logger

