# init_database.py
# 2024-03-01, JK
# Create a SQLite database and a table grade with data from a CSV file.
import sqlite3
import yaml
import os
import csv


filename_config = "config.yaml"

# Load filename_config into variable config
with open(filename_config, "r") as file:
    config = yaml.safe_load(file)

# Define the filename for the SQLite database
filename_sqlite = config["filenames"]["filename_db"]
filename_csv = config["filenames"]["filename_csv"]

# Del. file filename_sqlite if exists
if os.path.exists(filename_sqlite):
    os.remove(filename_sqlite)

# Connect to the SQLite database. This will create the database file if it
# does not exist
conn = sqlite3.connect(filename_sqlite)
cursor = conn.cursor()

# Create a cursor object using the connection
cur = conn.cursor()

# Read the CSV file to determine its structure
with open(filename_csv, "r") as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)  # Read the first row to get the headers
    types = next(reader)  # Read the second row to get the data types

    # Adjust the CREATE TABLE statement to use the provided data types
    columns_with_types = ", ".join([f"{headers[i]} {types[i]}" for i in range(len(headers))])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS grades ({columns_with_types})")

    # Prepare the INSERT INTO statement
    placeholders = ", ".join(["?"] * len(headers))
    insert_sql = f"INSERT INTO grades ({', '.join(headers)}) VALUES ({placeholders})"

    # Insert data from CSV to the table, skipping the first data row since it's types
    for row in reader:
        cursor.execute(insert_sql, row)

# Commit the changes
conn.commit()

# Close the connection
conn.close()
