#!/bin/bash
#every 30 min

rnn_home=~/mtg-rnn
output_home=~/mtgencode/cards

# setting output parameters
length=10000
temperature=0.5

## */30 * * * * ~/mtgencode/scripts/crons/make_output.sh 
if [[ $(pgrep -l 'luajit' | sed s/'[0-9]* '// ) =~ 'luajit' ]]; then
        echo Training running, exiting cron
        exit 0
fi

cd $rnn_home

for folder in $( ls cv); do
        echo $folder
        #I have my folders labeled by' {data_dir}-{rnn_size}_{dropout}"
# I can't decide of I want to remove {rnn_size} and {dropout} from output
#folder name
##      dir_name=$(echo $folder | sed s/-[1-9][1-9][1-9]_0.[0-9]*//g)
        dir_name=$folder
        if [ ! -e $output_home/$dir_name ]; then
                mkdir $output_home/$dir_name
        fi
        for file in $( ls cv/$folder); do
                o_file=$(echo $file | sed s/lm_lstm_epoch/e/)
                o_file=$(echo ${o_file} | sed s/_[0-9].[0-9]*//g)
                o_file=$(echo ${o_file} | sed s/.t7//)
                o_file=$(echo ${o_file}-${temperature})
                #if file exists don't make a new one
                if [ -e $output_home/$dir_name/$o_file/output.txt ];then
                        #echo "output for $file already exists"
                        continue
                fi
                #if the directory doesn't exist make it
                if [ ! -e ./$output_home/$dir_name/$o_file ]; then
                        mkdir $output_home/$dir_name/$o_file
                fi
                th $rnn_home/sample_hs_v3.lua cv/$folder/$file -gpuid -1 -temperature $temperature -length $length | tee $output_home/$dir_name/$o_file/output.txt
        done
done
# rsync to remote storage device
rsync -hruv -e 'ssh -p 2022' $output_home host@ip:/mtgencode/cards
