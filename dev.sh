#!/bin/bash

./ve/bin/twistd -n cyclone --app=echidna.demo.server.DemoServer --port=8888 --appopts=/tmp/dev.yaml
