#!/bin/bash
for i in {0..9}
do
  echo "copy hedgi.py and utils.py to ~ at 10.0.0.8$i"
  scp ~/hedgi.py ubuntu@10.0.0.8$i:.
  scp ~/utils.py ubuntu@10.0.0.8$i:.

done
