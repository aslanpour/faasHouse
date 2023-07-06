#!/bin/bash
for i in {0..9}
do
	echo "Try to reboot 10.0.0.8$i"
	ssh ubuntu@10.0.0.8$i "sudo reboot"
	
done
