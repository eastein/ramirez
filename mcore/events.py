import time
import Queue
import itertools
import heapq

def tick() :
	return int(time.time() * 1000)

class Processor :
	def __init__(self) :
		self.pq = []
		self.counter = itertools.count(0)
		self.eq = Queue.Queue()

	def _add_event(self, e) :
		new_entry = [e.ms, next(self.counter), e]
		heapq.heappush(self.pq, new_entry)
	
	def _get_event(self) :
		ms, count, e = heapq.heappop(self.pq)
		return e

	def add(self, e) :
		self.eq.put(e)

	def do(self) :
		next_event = None
		now = tick()

		try :
			next_event = self._get_event()
		except IndexError :
			next_event = self.eq.get()


		wait = max(0, next_event.ms - now)

		if wait > 0 :
			# it's not yet, we're not running behind.
			try :
				# wait for up to the amount of time left for something else to interrupt..
				q_event = self.eq.get(timeout=wait/1000.0)
				# we actually got a new event. Which one is first?
				if q_event.ms < next_event.ms :
					# the new one we just got is newer, so it gets to go.
					self._add_event(next_event)
					next_event = q_event
				else :
					self._add_event(q_event)

				# now next_event is the newest event but the interrupt from a newly added event
				# may mean that next_event shouldn't run yet.

				if next_event.ms > tick() :
					# yeah, it's not yet. Put it back on the queue and mark it to not run.
					self._add_event(next_event)
					next_event = None
			except Queue.Empty :
				pass

		# if now_event hasn't been set to None, we're supposed to handle it now.
		if next_event :
			# now we will handle the event.
			next_event.handle()

class Processable(object) :
	def __init__(self, processor=None) :
		self.processor = processor

class Event :
	def __init__(self, ms) :
		self.ms = ms

	def __repr__(self, extra=None) :
		if extra :
			return 'Event<ms=%d%s>' % (self.ms, extra)
		else :
			return 'Event<ms=%d>' % self.ms

	def handle(self) :
		print 'handling event %s' % self

class SampleEvent(Event) :
	def __init__(self, ms, s) :
		Event.__init__(self, ms)
		self.sensor = s

	def __repr__(self) :
		return Event.__repr__(self, ' sensor=%s' % self.sensor)

	def handle(self) :
		print 'sampling %s' % self.sensor
		self.sensor.sample()
