#!/bin/bash

timestamp=`date '+%s'`
start=$timestamp
while [ 1 ]
do
	echo $start $timestamp

    ColdInput=$((RANDOM%25+5))
    CircOut=$((RANDOM%75+5))
    CircReturn=$((RANDOM%75+5))
    BasementTemp=$((RANDOM%30+10))
    ToHeater=$((RANDOM%100+0))
    FromHeater=$((RANDOM%100+0))
    HotOut=$((RANDOM%75+5))
    WaterGals=$((RANDOM%55+0))

    rrdtool updatev hotwater.rrd $timestamp:$ColdInput:$CircOut:$CircReturn:$BasementTemp:$ToHeater:$FromHeater:$HotOut:$WaterGals
    timestamp=`expr $timestamp + 30`
done

