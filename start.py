#!/usr/bin/env python3
"""
Launch script - Run from project root.
"""
import sys
import os

# Change to project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Run as module
os.system(f'{sys.executable} -m src.main')
