#!/bin/bash

declare -A up_times

for i in {80..89}; do
    ip="10.0.0.$i"
    uptime=$(ssh ubuntu@"$ip" 'uptime -p')
    up_times["$ip"]=$uptime
done

for ip in "${!up_times[@]}"; do
    printf "%s: %s\n" "$ip" "${up_times[$ip]}"
done | sort -k3
