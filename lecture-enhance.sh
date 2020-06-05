#!/usr/bin/env bash
for i in "$@"
do
  python3.7 lecture-enhance.py input "$i" output "${i%.*} fixed.mp4"
done
