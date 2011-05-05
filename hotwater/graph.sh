#!/bin/bash

#ColdInput,CircReturn,BasementTemp,ToHeater,FromHeater,HotOutput

WHEN=`date '+%Y%m%d-%H:%M:%S'`
RRD_FILE=/home/bill/projects/hotwater/hotwater.rrd

rrdtool graph /tmp/24h-$WHEN.png -t "24 hours, Celsius" -w 800 -h 400 \
--end now --start end-86400s \
DEF:ColdInput=$RRD_FILE:ColdInput:AVERAGE \
DEF:CircReturn=$RRD_FILE:CircReturn:AVERAGE \
DEF:HotOutput=$RRD_FILE:HotOutput:AVERAGE \
DEF:ToHeater=$RRD_FILE:ToHeater:AVERAGE \
DEF:FromHeater=$RRD_FILE:FromHeater:AVERAGE \
DEF:BasementTemp=$RRD_FILE:BasementTemp:AVERAGE \
DEF:WaterGals=$RRD_FILE:WaterGals:AVERAGE \
LINE1:ColdInput#0000FF:"ColdInput\l" \
LINE2:CircReturn#00C000:"CircReturn\l" \
LINE3:HotOutput#FF0000:"HotOutput\l" \
LINE4:ToHeater#FFFF00:"ToHeater\l" \
LINE5:FromHeater#33CC99:"FromHeater\l" \
LINE6:BasementTemp#000000:"BasementTemp\l" \
LINE7:WaterGals#0000AF:"WaterGals\l" > /dev/null 2>&1

rrdtool graph /tmp/loss-$WHEN.png -t "24 hours, Celsius" -w 800 -h 400 \
--end now --start end-86400s \
DEF:ColdInput=$RRD_FILE:ColdInput:AVERAGE \
DEF:HotOutput=$RRD_FILE:HotOutput:AVERAGE \
DEF:CircReturn=$RRD_FILE:CircReturn:AVERAGE \
DEF:BasementTemp=$RRD_FILE:BasementTemp:AVERAGE \
LINE1:ColdInput#0000FF:"ColdInput\l" \
LINE2:HotOutput#FF0000:"HotOutput\l" \
LINE3:CircReturn#00C000:"CircReturn\l" \
LINE4:BasementTemp#000000:"BasementTemp\l" > /dev/null 2>&1

rrdtool graph /tmp/1h-$WHEN.png -t "1 hour, Celsius" -w 800 -h 400 \
--end now --start end-3600s \
DEF:ColdInput=$RRD_FILE:ColdInput:AVERAGE \
DEF:CircReturn=$RRD_FILE:CircReturn:AVERAGE \
DEF:HotOutput=$RRD_FILE:HotOutput:AVERAGE \
DEF:ToHeater=$RRD_FILE:ToHeater:AVERAGE \
DEF:FromHeater=$RRD_FILE:FromHeater:AVERAGE \
DEF:BasementTemp=$RRD_FILE:BasementTemp:AVERAGE \
DEF:WaterGals=$RRD_FILE:WaterGals:AVERAGE \
LINE1:ColdInput#0000FF:"ColdInput\l" \
LINE2:CircReturn#00C000:"CircReturn\l" \
LINE3:HotOutput#FF0000:"HotOutput\l" \
LINE4:ToHeater#FFFF00:"ToHeater\l" \
LINE5:FromHeater#33CC99:"FromHeater\l" \
LINE6:BasementTemp#000000:"BasementTemp\l" \
LINE7:WaterGals#0000AF:"WaterGals\l" > /dev/null 2>&1

exit 0
