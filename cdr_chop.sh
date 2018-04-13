#!/bin/bash

#### Author: C. Barela
#### Usage: ./cdr_chop.sh {CSV filename download from Etage} {date}
#### Script assumes that it would extract data for the previous day,
#### unless hardcoded in dateyesterday variable
#### Outputs: a CSV file containing all the transactions for a particular site/BTS


cdr_file=$1
dateyesterday=$2

# input the site uuids here
site1=""
site2=""
site3=""
site4=""
site5=""
site6=""
site7=""

eval "bts_uuid=\$$2"
echo "Generating all CDRs for" $2 $bts_uuid

outfile="vbts_konekt_"$2"_"$dateyesterday".csv"
header="Transaction ID,Day,Time,Time Zone,Subscriber IMSI,BTS Identifier,BTS Name,Type of Event,Description,From Number,To Number,Billable Call Duration (sec),Total Call Duration (sec),Tariff (PHP),Cost (PHP),Prior Balance (PHP),Final Balance (PHP),Bytes Uploaded,Bytes Downloaded"

echo $header > $outfile
cat $cdr_file | grep $dateyesterday | egrep $bts_uuid >> $outfile    
