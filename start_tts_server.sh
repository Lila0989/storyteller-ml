#!/bin/bash
# This is a helpful script for local development using Docker images.

cd models/tts
source python/bin/activate
./vocodes_server.py
