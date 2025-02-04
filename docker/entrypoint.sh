#!/bin/bash

# Start the run once job.
echo "Docker container has been started"

declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

wget https://raw.githubusercontent.com/hammad93/hurricane-server/main/hurricane_satellites.ipynb

pip install ipython
pip install nbformat
ipython --TerminalIPythonApp.file_to_run=hurricane_satellies.ipynb
