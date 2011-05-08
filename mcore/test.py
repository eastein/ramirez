import dbi,time
s = dbi.Trace('test',"test.db", 5000, 1000, 0)
s.write(1)
t = dbi.tick() + 300
time.sleep(2)
print s.read(t).result()
