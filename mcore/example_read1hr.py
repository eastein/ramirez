import trace
import events

s = trace.Trace('test',"test.db", 5000, 1000, 0)
now = events.tick()
print s.read(now - 1000 * 3600, now).result()
