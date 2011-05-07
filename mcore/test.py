import dbi,time
s = dbi.Trace('test',"test.db", 5000, 1000, 0)
s.write(1)
t = int(time.time() * 1000) + 300
time.sleep(2)
print s.read(t).result()
