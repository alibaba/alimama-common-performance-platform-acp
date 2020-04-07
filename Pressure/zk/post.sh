#!/bin/bash

sudo sed -i 's/net.ipv4.tcp_syncookies = 0/net.ipv4.tcp_syncookies = 1/g'  /etc/sysctl.conf
sudo sysctl net.ipv4.tcp_syncookies=1
sudo sysctl -w
