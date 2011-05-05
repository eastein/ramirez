rrdtool create hotwater.rrd --step 30 \
         DS:ColdInput:GAUGE:60:5:30 \
         DS:CircReturn:GAUGE:60:5:80 \
         DS:BasementTemp:GAUGE:60:10:40 \
         DS:ToHeater:GAUGE:60:0:100 \
         DS:FromHeater:GAUGE:60:5:100 \
         DS:HotOutput:GAUGE:60:5:80 \
         DS:WaterGals:COUNTER:60:0:55 \
		 RRA:LAST:0.5:1:5 \
         RRA:AVERAGE:0.25:10:12 \
         RRA:AVERAGE:0.25:120:24 \
         RRA:AVERAGE:0.25:2880:7 \
         RRA:AVERAGE:0.25:20160:4 \
         RRA:AVERAGE:0.25:80640:12 \
         RRA:MIN:0.25:120:24 \
         RRA:MAX:0.25:120:24

