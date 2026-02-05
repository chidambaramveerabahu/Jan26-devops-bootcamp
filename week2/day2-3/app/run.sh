#!/bin/bash


# create a virtual environment
python3 -m venv .venv

# activate the virtual environment
source .venv/bin/activate
# install dependencies
pip install -r requirements.txt

# run the application
gunicorn -w 4 -b 0.0.0.0:8000 app:app &

# run nginx
nginx -g "daemon off;"
