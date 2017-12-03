#!/bin/sh
ver=$(./gen-ver.sh)
docker build -t baverman/telenot:$ver .
docker push baverman/telenot:$ver
