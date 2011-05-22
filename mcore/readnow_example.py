import trace
import events

s = trace.Trace('test',"test.db", 5000, 1000, 0)
print s.read(events.tick()).result()
