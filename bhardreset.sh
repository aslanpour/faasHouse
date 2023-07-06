#!/bin/bash
echo "Only 81 -->80, 82--> 81, 84-->83 works"
# Prompt user for source and destination server IP addresses
read -p "Enter the source server IP address: " SOURCE_IP
# read -p "Enter the destination server IP address: " DESTINATION_IP
USER_NAME="ubuntu"

# Get current server IP address
CURRENT_IP=$(hostname -I | awk '{print $1}')

# Copy Python script to source server
ssh "$USER_NAME@$SOURCE_IP" << EOF
sudo bash -c 'cat > restart_pi.py' << EOL
#!/usr/bin/env python3
#connect a female wire to Pin 17 of a controller Pi 3 (only worked on Pi 3) on one end and a the male end to the 'Run' pin/hole of the Pi 3 that is going to be restarted.
#Run this code on the controller Pi to restart the other Pi.
#if not, run as sudo

import RPi.GPIO as GPIO
import time
PIN=17
GPIO.setmode(GPIO.BCM)  # set the pin numbering scheme to BCM
GPIO.setup(PIN, GPIO.OUT)  # set up GPIO 17 as an output

GPIO.output(PIN, GPIO.LOW)  # trigger the restart by pulling GPIO 17 low
time.sleep(1)  # wait for 1 second
GPIO.output(PIN, GPIO.HIGH)  # release GPIO 17 to allow the Raspberry Pi to start up
# release the GPIO channel
GPIO.cleanup(PIN)
EOL
EOF

# Run Python script on source server
ssh "$USER_NAME@$SOURCE_IP" "sudo python3 ~/restart_pi.py"
