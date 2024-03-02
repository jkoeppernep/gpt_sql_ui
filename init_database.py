# init_database.py
# 2024-03-01, JK
# Create a SQLite database and a table grade with data from a CSV file.
import sqlite3
import os
import csv
from utilities import load_config, create_conn_and_cursor


# Load the configuration from the config.yaml file
config = load_config()

filename_sqlite = config["filenames"]["filename_db"]
filename_csv = config["filenames"]["filename_csv"]

# Delete the file filename_sqlite if it exists
if os.path.exists(filename_sqlite):
    os.remove(filename_sqlite)

# Connect to the SQLite database (this creates the database file if it does not exist)
conn, cursor = create_conn_and_cursor()

# Read the CSV file to determine its structure
with open(filename_csv, "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=';')  # Ensure the delimiter is set to semicolon
    headers = next(reader)  # Read the first row to get the headers
    types = next(reader)  # Read the second row to get the data types, correcting them as necessary

    # Correct data types for SQLite and replace semicolons with commas
    corrected_types = [t.replace("String", "TEXT").replace("Char", "TEXT").replace("INT", "INTEGER") for t in types]
    columns_with_types = ", ".join([f"{headers[i]} {corrected_types[i]}" for i in range(len(headers))])

    # Create the grades table with the corrected column definitions
    cursor.execute(f"CREATE TABLE IF NOT EXISTS grades ({columns_with_types})")

    # Prepare the INSERT INTO statement
    placeholders = ", ".join(["?"] * len(headers))
    insert_sql = f"INSERT INTO grades ({', '.join(headers)}) VALUES ({placeholders})"

    # Insert data from CSV into the table, skipping the second row (data types)
    for row in reader:
        cursor.execute(insert_sql, row)

# Commit the changes to the database
conn.commit()

# Optional: Print all data in the table to verify
cursor.execute("SELECT * FROM grades")
# print the data with 1 line per row
for row in cursor.fetchall():
    print(row)

# Close the database connection
conn.close()
