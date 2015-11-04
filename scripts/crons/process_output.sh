#!/bin/bash
# every 5 min

## */30 * * * * ~/mtgencode/scripts/crons/process_output.sh 

cd ~/mtgencode/cards
pwd
for folder in $(ls); do
#	echo $folder
	for sub in $( ls $folder );do 
#		echo $folder/$sub
		if [ ! -d $folder/$sub ]; then
			continue
		fi
		if [ ! -e ./$folder/$sub/summary.txt ]; then
			../scripts/summarize.py -a -v $folder/$sub/output.txt > summary.txt
		fi
		if [ ! -e  ./$folder/$sub/cards.txt ]; then
			../decode.py -v -f $folder/$sub/output.txt $folder/$sub/cards.txt
		fi
	done
done
