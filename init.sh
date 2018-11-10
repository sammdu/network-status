#!/bin/bash

# Sync Time with Google
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"
# Start Monitor
screen -d -m bash -c 'cd /home/pi/network-status; python3 ./nstat.py'
# Start Web Server
screen -d -m bash -c 'cd /home/pi/network-status/logs; sudo python3 -m http.server --bind 0.0.0.0 80'
# List 'screen' Sessions
screen -ls
