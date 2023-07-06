#!/bin/bash
for i in {0..9}
do
	OUTPUT=$(ssh ubuntu@10.0.0.8$i pgrep -f hedgi)
	if  [ -n "$OUTPUT" ] 
	then
		echo "Try to kill hedgi.py in 10.0.0.8$i"
		#ssh ubuntu@10.0.0.8$i pgrep -f hedgi | xargs kill 
		ssh ubuntu@10.0.0.8$i "kill -9 \$(ps -aux |grep hedg | awk '{print \$2}')"
	else
		 echo "hedgi.py was NOT running"
	fi
done
