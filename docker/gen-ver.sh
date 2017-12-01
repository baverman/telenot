#!/bin/bash
cat Dockerfile requirements.txt | md5sum | cut -b1-10
