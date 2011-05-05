#!/usr/bin/env python

import sys
import Config
import Log
import Mail
import time
import u12
from serial import Serial
from DS18B20 import DS18B20
import rrdtool

name = 'hotwater'

devices = {}
deviceList = []

def listDevices(conf, name):
	global devices, deviceList

	deviceList = conf.get(name, 'devices').rsplit(',')
	for device in deviceList:
		devices[device] = DS18B20(device, conf.get(device, 'ID'))

	return

conf = Config.Config('hotwater.conf')
log = Log.Log(conf, name)

log.info('Starting')


linkusb = Serial(
	port = conf.get(name, 'serialPort'),
	baudrate = int(conf.get(name, 'baudRate')),
	timeout = 0.1)
linkusb.setRTS(level = True)
linkusb.setDTR(level = True)

labjack = u12.U12()

listDevices(conf, name)
log.info('Devices: %s' % (deviceList))

rrdDb = conf.get(name, 'rrd.db')
rrdInterval = float(conf.get(name, 'rrd.interval'))

fromAddress = 'bill@manialabs.us'
alertToList = conf.get(name, 'alertToList').rsplit(',')
msgAlarm = Mail.MailMessage(
	'Water temp low',
	'Water temp low',
	fromAddress,
	alertToList
)
msgRecover = Mail.MailMessage(
	'Water temp OK',
	'Water temp OK',
	fromAddress,
	alertToList
)

alarmThreshold = float(conf.get(name, 'alarmThreshold'))
recoverThreshold = float(conf.get(name, 'recoverThreshold'))
log.debug('Initial settings: %0.1f, %0.1f, %s' % (alarmThreshold, recoverThreshold, alertToList))
alreadySentAlarm = 0

while True:
	cycleStart = time.time()

	rrdDS = ""
	for device in deviceList:
		devices[device].convert(linkusb)
		temp = devices[device].retrieveTemp(linkusb)
		rrdDS = rrdDS + ":%.1f" % (temp)
		if device == 'HotOutput':
			hotOutputTemp = temp

	cycleEnd = time.time()
	cycleTimestamp = (cycleEnd + cycleStart) / 2

	#
	# add the water gallons counter
	#
	rrdDS = "%d" % (int(cycleTimestamp)) + rrdDS + ":%d" % int(labjack.rawCounter()['Counter'])

	if hotOutputTemp <= alarmThreshold and alreadySentAlarm == 0:
		log.debug('Low water temp %.1f' % (hotOutputTemp))
		mta = Mail.MailTransport('SMTPHOST', 'USERNAME', 'PASSWORD')
		mta.sendMessage(msgAlarm)
		mta.done()
		alreadySentAlarm = 1
	else:
		if alreadySentAlarm == 1 and hotOutputTemp >= recoverThreshold:
			mta = Mail.MailTransport('SMTPHOST', 'USERNAME', 'PASSWORD')
			mta.sendMessage(msgRecover)
			mta.done()
			alreadySentAlarm = 0
			alarmThreshold = float(conf.get(name, 'alarmThreshold'))
			recoverThreshold = float(conf.get(name, 'recoverThreshold'))
			alertToList = conf.get(name, 'alertToList').rsplit(',')
			log.debug('New settings: %0.1f, %0.1f, %s' % (alarmThreshold, recoverThreshold, alertToList))
			del msgAlarm
			del msgRecover
			msgAlarm = Mail.MailMessage(
				'Water temp low',
				'Water temp low',
				fromAddress,
				alertToList
			)
			msgRecover = Mail.MailMessage(
				'Water temp OK',
				'Water temp OK',
				fromAddress,
				alertToList
			)
		
	rrdtool.update(rrdDb, rrdDS)
	log.debug(rrdDS)

	time.sleep(rrdInterval - (time.time() - cycleStart))

sys.exit(0)
