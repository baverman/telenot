#!/bin/sh
set -e
envfile=$(realpath ${1:?Envfile required})
shift

if [ -n "$1" ]; then
  curdir=$1
  mkdir -p $curdir
  cd $curdir
  shift
fi

source $envfile
name=${NAME:-$(basename $datadir)}
docker_args="--name=$name $DOCKER_OPTS $OPTS -u $UID:$GROUPS $IMAGE $CMD $@"
arg_hash=$(echo $docker_args | md5sum | cut -d' ' -f1)
cur_hash=$(docker inspect --format '{{ index .Config.Labels "arg.hash"}}' telenot-http || true)

if [ "$arg_hash" == "$cur_hash" ]; then
  docker restart $name
else
  docker stop $name || true
  docker rm $name || true
  exec docker run -d --restart=unless-stopped --label=arg.hash=$arg_hash $docker_args
fi
