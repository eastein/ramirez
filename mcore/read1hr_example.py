import trace
import events
import pprint

s = trace.Trace('test',"test.db", 5000, 1000, 0)
now = events.tick()
for tick in s.read(now - 1000 * 3600, now).result() :
	#pprint.pprint(tick.asdict)
	print tick
