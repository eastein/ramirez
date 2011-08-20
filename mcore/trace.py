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
	def __init__(self, trace, value, start_ms, end_ms, tick_ms, sample_err_allowed, tick_err_allowed_ms) :
		self.trace = trace
		self.value = value
		self.start_ms = start_ms
		self.end_ms = end_ms
		self.tick_ms = tick_ms
		self.sample_err_allowed = sample_err_allowed
		self.tick_err_allowed_ms = tick_err_allowed_ms

	@property
	def asdict(self) :
		return {
			'value' : self.value,
			'start_ms' : self.start_ms,
			'end_ms' : self.end_ms,
			'tick_ms' : self.tick_ms,
			'sample_err' : self.sample_err_allowed,
			'tick_err' : self.tick_err_allowed_ms
		}

	def __repr__(self) :
		asc_start = time.asctime(time.gmtime(self.start_ms / 1000))
		asc_end = time.asctime(time.gmtime((self.end_ms + self.tick_ms) / 1000))
		return 'Tick<of=%s, v=%d, f=%s UTC, t=%s UTC, tick=%d s_err=%d, t_err=%d>' % (self.trace, self.value, asc_start, asc_end, self.tick_ms, self.sample_err_allowed, self.tick_err_allowed_ms)

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
		return self.name

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
				return Tick(self, value, now_ms, now_ms, self.tick_ms, self.sample_err_allowed, self.tick_err_allowed_ms)
			else :
				at_ms = end_ms + tick_ms
				self.cursor.execute('update samples set end_ms = ? where id = ?', (at_ms, id))
				return Tick(self, value, start_ms, at_ms, self.tick_ms, self.sample_err_allowed, self.tick_err_allowed_ms)
		finally :
			self.conn.commit()

	def read(self, time_ms, end_time_ms=None) :
		self.waitsetup()
		return self.executor.submit(self._read, time_ms, end_time_ms)

	def _read(self, time_ms, end_time_ms=None) :
		rq = end_time_ms is not None
		if not rq :
			end_time_ms = time_ms

		sample = self.cursor.execute('select start_ms,end_ms,tick_ms,tick_err_allowed_ms,sample,sample_err_allowed from samples where start_ms>=(select min(t) from (select max(start_ms) t from samples where start_ms <= ? union select min(start_ms) t from samples where start_ms >= ?)) and start_ms <= ?', (time_ms,time_ms,end_time_ms)).fetchall()
		if not sample :
			if rq :
				return []
			else :
				return None

		if not rq :
			sample = sample[0]
			start_ms,end_ms,tick_ms,tick_err_allowed_ms,sample,sample_err_allowed = sample

			if time_ms > end_ms + tick_ms :
				return None

			return Tick(self, sample, start_ms, end_ms, tick_ms, sample_err_allowed, tick_err_allowed_ms)
		else :
			r = []
			for s in sample :
				start_ms,end_ms,tick_ms,tick_err_allowed_ms,value,sample_err_allowed = s
				if time_ms > end_ms + tick_ms :
					continue
				r.append(Tick(self, value, start_ms, end_ms, tick_ms, sample_err_allowed, tick_err_allowed_ms))
			return r
