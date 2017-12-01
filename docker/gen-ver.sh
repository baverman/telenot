#!/bin/bash
curdir=$(dirname $0)
cat $curdir/Dockerfile $curdir/requirements.txt | md5sum | cut -b1-10
