#!/usr/bin/env bash

VERSION="2.0.1"

docker build --platform linux/arm64 -t ghcr.io/luca-heitmann/hsh-grade-checker:$VERSION .
docker push ghcr.io/luca-heitmann/hsh-grade-checker:$VERSION
