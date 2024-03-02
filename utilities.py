# utilities.py
# 2024-03-01, JK
# This file provides utility functions for this project.
import yaml
import sqlite3
import datetime


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

def add_token_usage_to_db(conn, cursor, prompt_tokens, completion_tokens):
    current_datetime_utc = datetime.datetime.utcnow()
    date_timestamp_ms = int(current_datetime_utc.timestamp() * 1000)

    # 2. Add a row to the table with these 3 values
    insert_command = """
    INSERT INTO usage (date_timestamp_ms, prompt_tokens, completion_tokens)
    VALUES (?, ?, ?);
    """

    cursor.execute(insert_command, (date_timestamp_ms, prompt_tokens, completion_tokens))
    conn.commit()

def display_token_usage_in_sidebar(sql_query):
    conn, cursor = create_conn_and_cursor()

# Execute the query
    cursor.execute(sql_query)

# Fetch the result
    result = cursor.fetchone()

# Display the summed up values
    total_prompt_tokens = result[0] if result[0] is not None else 0
    total_completion_tokens = result[1] if result[1] is not None else 0

    conn.close()

    st.sidebar.write(f"Total prompt tokens: {total_prompt_tokens}")

    st.sidebar.write(f"Total completion tokens: {total_completion_tokens}")

    