#!/usr/bin/env bash

docker build -t ghcr.io/luca-heitmann/hsh-grade-checker .
docker push ghcr.io/luca-heitmann/hsh-grade-checker
