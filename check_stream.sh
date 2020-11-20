#!/usr/bin/env bash

########
# YouTube live broadcast monitor
##########

## arg management
youtube=''
verbose='false'

print_usage() {
    printf "Usage: ..."
}

while getopts 'y:v' flag; do
    case "${flag}" in
    # a) a_flag='true' ;;
    y) youtubeURL="${OPTARG}" ;;
    v) verbose='true' ;;
    *)
        print_usage
        exit 1
        ;;
    esac
done

if "$verbose"; then
    echo "going to check $youtubeURL"
fi

mkdir -p videostream/
cd videostream/

# Get YouTube Manifest 1
youtube-dl -4 -f 91 -g $youtubeURL >manifest1.txt
# Probe Manifest 1
ffprobe -v quiet -print_format json -show_streams "$(<manifest1.txt)" >json1.txt

sleep 2

youtube-dl -4 -f 91 -g $youtubeURL >manifest2.txt
ffprobe -v quiet -print_format json -show_streams "$(<manifest2.txt)" >json2.txt
# do we have a valid json

starttime=$(cat json1.txt | jq '.streams[].start_time')
if [ -z "$starttime" ]; then
    echo "$(date)" "Error: No start_time" "$starttime"
    exit 1
fi

# compare the ffprobe json, if they are the same, the live stream stopped
if cmp -s json1.txt json2.txt; then
    if "$verbose"; then
        echo "$(date)" "Stream Down"
    fi
    exit 1
else
    if "$verbose"; then
        echo "$(date)" "Stream Up"
    fi
fi
