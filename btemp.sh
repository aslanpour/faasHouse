#!/bin/bash

log="alihasan"

for i in {0..9}
do
  id_node=$((i+1))
  id_node_str="${id_node}"
  log="${log}id${id_node_str}"
  echo "$log"
done

echo "$log"
