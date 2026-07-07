#!/usr/bin/env bash
# Start the virtualenv and the xbox controller mode. Prepare the xbox controller by turning it on prior to boot.
aplay audio/2860.wav
source .mecanum-robot/bin/activate
python3 xbox-controller-test.py
