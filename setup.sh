#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Initialize the database
python -c "from app import init_db; init_db()"

# Run the Flask app
export FLASK_APP=app.py
export FLASK_ENV=development
python -m flask run
