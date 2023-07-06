#!/bin/bash
#run
#./bcluster_info.sh 
#./bcluster_info.sh 5
#./bcluster_info.sh 5 node
#./bcluster_info.sh 5 node remote
#./bcluster_info.sh 5 notnode remote

if [[ $# -ge 1 ]]; then
    delay=$1
    TYPE=$2
    if [ -n "$3" ]; then
        REMOTE=$3
    fi
    while true 
    do
        if [ "$TYPE" = "node" ]; then
            if [ -n "$REMOTE" ]; then
                ssh ubuntu@10.0.0.90 tail -n 11 /home/ubuntu/logs/cluster_info/nodes.txt
            else
                tail -n 11 /home/ubuntu/logs/cluster_info/nodes.txt
            fi
        else
            if [ -n "$REMOTE" ]; then
                ssh ubuntu@10.0.0.90 tail -n 11 /home/ubuntu/logs/cluster_info/functions.txt
            else
                tail -n 11 /home/ubuntu/logs/cluster_info/functions.txt
            fi
        fi
        sleep $delay
    done

else
    if [ -n "$REMOTE" ]; then
        ssh ubuntu@10.0.0.90 tail -n 11 /home/ubuntu/logs/cluster_info/nodes.txt
        ssh ubuntu@10.0.0.90 tail -n 11 /home/ubuntu/logs/cluster_info/functions.txt
    else
        tail -n 11 /home/ubuntu/logs/cluster_info/nodes.txt
        tail -n 11 /home/ubuntu/logs/cluster_info/functions.txt
    fi
    
fi