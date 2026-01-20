#!/bin/bash

CURRENT_TIME=$(date +%Y%m%d%H%M%S)

git add .
git commit -m "build v0.2.0_$CURRENT_TIME"
git push