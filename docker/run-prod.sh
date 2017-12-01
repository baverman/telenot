#!/bin/sh
data=$1
curdir=$(realpath $(dirname $0))
src=$(realpath $curdir/..)
version=$($curdir/gen-ver.sh)
uid=$(id -u)
gid=$(id -g)
exec docker run -d -v $src:/app -v $data:/data -w /app -u $uid:$gid -e CONFIG=/data/config.py baverman/telenot:$version uwsgi --ini /app/uwsgi.ini
