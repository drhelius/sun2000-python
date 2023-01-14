#!/bin/bash

sudo docker run --name influxdb -d --restart always -p 8086:8086 -v influxdb:/var/lib/influxdb2 influxdb:2.6