#!/bin/sh -eux


for file in $*; do
    zcat $file | curl -X POST -H 'Content-Type: application/json' http://localhost:8001/train-movements/ --data @-
done
# zcat 0000000_2016-03-20T20:35:00Z_0003.json.gz | curl -X PUT -H 'Content-Type: application/json' http://localhost:8001/train-movements/1aa681f3-712e-4ee0-9a5e-1543034d92ab/ --data @-
