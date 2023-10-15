#! /bin/bash

if [ "$#" -ne 3 ]; then
    echo "Example usage: ./gather.sh <time_in_seconds> <limit> <pair>"
    echo "./gather.sh 1000 100 BTCUSDT"
    exit -1
fi
pair=$3
end=$((SECONDS+$1))
count=0
limit=$2
directory=data/$pair"_"$1_$2_`date +%s`


mkdir -p $directory

while true; do
    # Do what you want.
    curl -s "https:/api1.binance.com/api/v3/depth?symbol=$pair&limit=$limit" > $directory/data$count.json
    echo Gathering sample $count
    let count++;
done


echo Finished.

