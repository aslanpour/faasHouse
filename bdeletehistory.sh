#!/bin/bash

# Loop through all the commands in the history
for i in $(seq $(history | wc -l)); do

  # Get the command at the current line number
  cmd=$(history | sed -n "${i}p")

  # Get the number of characters in the command
  count=$(echo $cmd | wc -c)

  # If the command contains more than 300 characters, delete it
  if [ $count -gt 300 ]; then
    history -d $(echo $cmd | cut -d' ' -f1)
  fi
done
