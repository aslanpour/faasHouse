#!/bin/bash

if [[ $# -eq 1 ]]; then
  delay=$1
  while true; do
    echo "Start at $(date)"
    for i in {80..90}; do
      ip="10.0.0.$i"
      if ping -c 1 $ip &> /dev/null; then
        echo "$ip is up"
      else
        echo "$ip is down ************"
      fi
    done
    echo "sleep for $delay sec"
    sleep $delay
  done
else
  for i in {80..90}; do
    ip="10.0.0.$i"
    if ping -c 1 $ip &> /dev/null; then
      echo "$ip is up"
    else
      echo "$ip is down"
    fi
  done
fi
