import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the 'app' object from 'main.py' and alias it as 'application'
# Passenger looks for an object named 'application'
from main import app as application