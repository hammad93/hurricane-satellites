#!/bin/bash

# Start the run once job.
echo "Docker container has been started"

declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

source /opt/venv/bin/activate
pip install -r /output/hurricane-satellites/requirements.txt
python /output/hurricane-satellites/test.py
# pip install jupyter
# jupyter lab --allow-root --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token=''
# pip install ipython
# pip install nbformat
# ipython --TerminalIPythonApp.file_to_run=hurricane_satellites.ipynb
