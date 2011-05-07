import dbi,time
s = dbi.Trace('test',"test.db", 5000, 1000, 0)
s.write(1);print s.read(int(time.time()*1000))
