#!/bin/bash

echo "{\"trains\":["

train_ind=0
for train in `cat train_numbers.txt`; do
  line_ind=0
  result=""
  while read -r line; do
    if [ "$line_ind" = "2" ]; then
      time=`echo $line | cut -d ">" -f2 | cut -d "+" -f1`
      station=`echo $line | cut -d "/" -f2 | cut -d "/" -f1`
      result="$result\n{\"time\":\"$time\",\"station\":\"$station\"},"
    fi
    line_ind=$((line_ind+1))
    if [ "$line_ind" == "4" ]; then
      line_ind=0
    fi
  done < <(grep -r -C1 ">$train<" raw_data/)

  if [ "$train_ind" != "0" ]; then
    echo ","
  fi
  train_ind=$((train_ind+1))

  echo "{\"id\":$train,\"route\":["
  echo -e $result | grep "2017-05-16" | sort | uniq
  echo "]}"
done

echo "]}"
