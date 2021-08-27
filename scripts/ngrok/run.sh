#!/bin/bash

port=$1

if [ -z $port ]; then
  port=8000
fi

ngrok http $port -bind-tls=true
