# utilities.py
# 2024-03-01, JK
# This file provides utility functions for this project.
import yaml
import sqlite3


filename_config = "config.yaml"

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    
    return config

config = load_config()

def create_conn_and_cursor():
    conn = sqlite3.connect(config["filenames"]["filename_db"])
    
    cursor = conn.cursor()

    return conn, cursor