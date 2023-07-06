#!/bin/bash
for i in {0..9}
do
	echo "Run hedgi.py on 10.0.0.8$i in background"
	ssh ubuntu@10.0.0.8$i  nohup python3 hedgi.py > hedgi.out 2> hedgi.err < /dev/null & echo "$i done"
done
