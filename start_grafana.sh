#!/bin/bash

sudo docker run --name grafana -d --restart always -p 3000:3000 -v grafana:/var/lib/grafana \
  -e "GF_SECURITY_ALLOW_EMBEDDING=false" \
  -e "GF_USERS_ALLOW_SIGN_UP=false" \
  -e "GF_AUTH_ANONYMOUS_ENABLED=false" \
  -e "GF_SERVER_PROTOCOL=https" \
  -e "GF_SERVER_CERT_FILE=/var/lib/grafana/ssl/grafana.crt" \
  -e "GF_SERVER_CERT_KEY=/var/lib/grafana/ssl/grafana.key" \
  grafana/grafana:latest