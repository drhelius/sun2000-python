#!/bin/bash

sudo docker run --name grafana -d --restart always -p 3000:3000 grafana/grafana:latest