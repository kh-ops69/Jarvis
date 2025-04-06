#!/bin/bash

echo "Starting installation for Linux..."

# Update package list
sudo apt-get update

pip install --upgrade pip

# make sure essential tool are installed
sudo apt install python3-dev python3-pip python3-wheel build-essential alsa-utils
# install port audio
sudo apt-get install portaudio19-dev python-pyaudio python3-pyaudio
# install chromedriver misc
sudo apt install libgtk-3-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2t64
# install wheel
pip install --upgrade pip setuptools wheel
# install docker compose
sudo apt install docker-compose
# Install Python dependencies from requirements.txt
pip3 install -r requirements.txt
# Install Selenium for chromedriver
pip3 install selenium

echo "Installation complete for Linux!"