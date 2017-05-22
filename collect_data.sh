#!/bin/bash

for station in `cat stations_codes_nl.txt`; do 
  output_dir="raw_data"
  mkdir -p "$output_dir/$station"
  timestamp=`date +"%Y_%m_%d_%H_%M"`
  filename="$output_dir/$station/timetable-$station-$timestamp.xml"
  echo $filename
  curl --user USER:PSWD https://webservices.ns.nl/ns-api-avt?station=$station > $filename
  sleep 1
done
