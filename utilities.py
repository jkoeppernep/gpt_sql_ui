# utilities.py
# 2024-03-01, JK
# This file provides utility functions for this project.
import yaml


filename_config = "config.yaml"


def load_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    
    return config
