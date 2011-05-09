'''
Ramirez is a home monitoring application.

Copyright 2007-2010 Eric Stein
License: GPL2/GPL3, at your option.  For details see LICENSE.
'''

import time
import events
import concurrent.futures as futures
import pysqlite2.dbapi2 as sqlite

def fupack(t) :
	(a, ) = t
	return a

class Tick(object) :
	def __init__(self, trace, value, when_ms, sample_err_allowed, tick_err_allowed_ms) :
		self.trace = trace
		self.value = value
		self.when_ms = when_ms
		self.sample_err_allowed = sample_err_allowed
		self.tick_err_allowed_ms = tick_err_allowed_ms

	def __repr__(self) :
		return 'Tick<of=%s, value=%d, when=%s UTC, s_err=%d, t_err=%d>' % (self.trace, self.value, time.asctime(time.gmtime(self.when_ms / 1000)), self.sample_err_allowed, self.tick_err_allowed_ms)

class Trace(object) :
	'''
	Trace database layer.  A trace here does not know how to measure, but can record.
	A sensor has a type, and that is all.
	'''

	def __init__(self, name, dbfilename, tick_ms, tick_err_allowed_ms, sample_err_allowed, executor=None) :
		self.name = name
		self.tick_ms = tick_ms
		self.tick_err_allowed_ms = tick_err_allowed_ms
		self.sample_err_allowed = sample_err_allowed
		if executor :
			self.executor = executor
		else :
			self.executor = futures.ThreadPoolExecutor(max_workers=1)

		self._setup = self.executor.submit(self._connection_setup, dbfilename)

	def waitsetup(self) :
		if not self._setup.done() :
			futures.wait([self._setup])

	def _connection_setup(self, dbfilename) :
		self.conn = sqlite.connect(dbfilename)
		self.cursor = self.conn.cursor()

		try :
			i = self.cursor.execute('select count(*) from samples')
		except sqlite.OperationalError :
			self._create_tables()
			self.conn.commit()

	def __repr__(self) :
		return 'Trace<%s>' % self.name

	def _create_tables(self) :
		self.cursor.execute('create table samples (id integer primary key autoincrement, start_ms integer, end_ms integer, tick_ms integer, tick_err_allowed_ms integer, sample integer, sample_err_allowed integer)')
		self.cursor.execute('create index samples_start_ms on samples(start_ms)')
		self.cursor.execute('create index samples_end_ms on samples(end_ms)')

	def write(self, value) :
		self.waitsetup()
		return self.executor.submit(self._write, value)

	def _write(self, value) :
		"""
		Must tolerate tick_error_tolerate ms of drift.
		"""

		now_ms = events.tick()

		# when the last measurement should be, if we've had no timing or restart problems
		end_low = now_ms - self.tick_err_allowed_ms - self.tick_ms
		end_high = now_ms + self.tick_err_allowed_ms - self.tick_ms
		last_measurement = self.cursor.execute('select id,start_ms,end_ms,tick_ms,tick_err_allowed_ms,sample,sample_err_allowed from samples where end_ms <= ? and end_ms >= ? order by end_ms desc', (end_high, end_low)).fetchall()

		create = True
		if last_measurement :
			create = False
			
			id,start_ms,end_ms,tick_ms,tick_err_allowed_ms,sample,sample_err_allowed = last_measurement[0]

			create = create or tick_ms != self.tick_ms			
			create = create or tick_err_allowed_ms != self.tick_err_allowed_ms
			create = create or sample_err_allowed != self.sample_err_allowed
			create = create or value > sample + sample_err_allowed or value < sample - sample_err_allowed
		try :
			if create :
				self.cursor.execute('insert into samples (start_ms,end_ms,tick_ms,tick_err_allowed_ms,sample,sample_err_allowed) values (?,?,?,?,?,?)', (now_ms, now_ms, self.tick_ms, self.tick_err_allowed_ms, value, self.sample_err_allowed))
				return Tick(self, value, now_ms, self.sample_err_allowed, self.tick_err_allowed_ms)
			else :
				self.cursor.execute('update samples set end_ms = ? where id = ?', (end_ms + tick_ms, id))
				return Tick(self, value, end_ms + tick_ms, self.sample_err_allowed, self.tick_err_allowed_ms)
		finally :
			self.conn.commit()

	def read(self, time_ms) :
		self.waitsetup()
		return self.executor.submit(self._read, time_ms)

	def _read(self, time_ms) :
		sample = self.cursor.execute('select start_ms,end_ms,tick_ms,tick_err_allowed_ms,sample,sample_err_allowed from samples where start_ms=(select max(start_ms) from samples where start_ms <= ?)', (time_ms,)).fetchall()
		if not sample :
			return None
		sample = sample[0]

		start_ms,end_ms,tick_ms,tick_err_allowed_ms,sample,sample_err_allowed = sample

		if time_ms > end_ms + tick_ms :
			return None

		when_ms = time_ms - ((time_ms - start_ms) % tick_ms)

		return Tick(self, sample, when_ms, sample_err_allowed, tick_err_allowed_ms)
