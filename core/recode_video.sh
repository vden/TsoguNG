#!/bin/sh

INPUT_FILE="$1"
OUTPUT_FILE="$2"

FFMPEG="/usr/bin/ffmpeg"

$FFMPEG -y -i "$INPUT_FILE" -ar 44100 -acodec libmp3lame -ar 44100 -s 530x400 -b 640k "$OUTPUT_FILE.tmp.flv"
rm -f "$INPUT_FILE"
mv "$OUTPUT_FILE.tmp.flv" "$OUTPUT_FILE"
