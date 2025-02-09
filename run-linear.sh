#!/bin/sh
# Usage: ./run-linear.sh [cleanup] [save]

save=false
cleanup=false
for arg in "$@"
do
    if [ "$arg" == "cleanup" ]
    then
        cleanup=true
    elif [ "$arg" == "save" ]
    then
        save=true
    fi
done

if [ $cleanup == true ]
then
    rm -rf linear-result
    mkdir -p linear-result
fi

trap "exit" INT
trap "kill 0" EXIT

num_types=3
num_traders=500
run_time=$((10*60))

function log {
    echo -e "\033[1;32m`date "+%Y-%m-%d %H:%M:%S"`\t$1\033[0m"
}

function run {
    result_file="linear-result/$1-p.result"
    json_file="linear-result/$1-p.json"
    log_file="linear-result/$1-p.log"

    if [ -f $json_file ]
    then
        log "Loading from $json_file..."
        go run cmd/main.go -load-from=$json_file > $result_file 2> $log_file
        log "Loaded from $json_file."
    else
        alpha=$(echo "$1/100" | bc -l)
        log "Running with alpha=$1%..."
        go run cmd/main.go -type=$num_types -time=$run_time -trader=$num_traders -random=$num_traders -alpha=$alpha -save-to=$json_file > $result_file 2> $log_file
        log "Run with alpha=$1% finished."
    fi

    result_file="linear-result/$1-num-bad.result"
    json_file="linear-result/$1-num-bad.json"
    log_file="linear-result/$1-num-bad.log"

    if [ -f $json_file ]
    then
        log "Loading from $json_file..."
        go run cmd/main.go -load-from=$json_file > $result_file 2> $log_file
        log "Loaded from $json_file."
    else
        num_bad=$(echo "$1/100*$num_traders" | bc -l | awk '{print int($1)}')
        log "Running with $1% bad traders..."
        go run cmd/main.go -type=$num_types -time=$run_time -trader=$num_traders -save-to=$json_file -bad=$num_bad > $result_file 2> $log_file
        log "Run with $1% bad traders finished."
    fi

    result_file="linear-result/$1-num-random.result"
    json_file="linear-result/$1-num-random.json"
    log_file="linear-result/$1-num-random.log"

    if [ -f $json_file ]
    then
        log "Loading from $json_file..."
        go run cmd/main.go -load-from=$json_file > $result_file 2> $log_file
        log "Loaded from $json_file."
    else
        num_random=$(echo "$1/100*$num_traders" | bc -l | awk '{print int($1)}')
        log "Running with $1% random traders..."
        go run cmd/main.go -type=$num_types -time=$run_time -trader=$num_traders -random=$num_random -save-to=$json_file > $result_file 2> $log_file
        log "Run with $1% random traders finished."
    fi
}

for i in {1..10}
do
    for j in $(seq $i 10 100)
    do
        run $j
    done &
done

wait

if [ $save == true ]
then
    rm -rf linear-output linear-output.zip && mkdir -p linear-output
    cp linear-result/*.result linear-output/
    zip -r linear-output.zip linear-output && rm -rf linear-output
    log "Output saved to linear-output.zip."

    rm -rf linear-backup linear-backup.zip && mkdir -p linear-backup
    cp linear-result/*.json linear-backup/
    zip -r linear-backup.zip linear-backup && rm -rf linear-backup
    log "Backup saved to linear-backup.zip."
fi

log "All runs finished!"