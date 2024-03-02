"""
app.py
2024-03-01, JK

This app
- requires a sqlite3 database file created by init_database.py
- copies the database file (filename_db) to a new file with filename given in config.yaml, filename_dispoable_db
- inits a streamlit app with title given in config.yaml, title
- provides a textbox so the user can enter a question in natural language
- this wuestion is translated into a SQL query using a LLM
- the query is executed on the database
- the result is displayed in a table
- also the SQL query is displayed
- the token usage is displayed in the sidebar

It was developed for Macomwsia seminar *NAMA*, 2024, SS.
"""
import streamlit as st
from openai import OpenAI
import re

from utilities import load_config, create_conn_and_cursor, add_token_usage_to_db


# ------------------------------
## Functions
# ------------------------------

# ------------------------------
## Application
# ------------------------------
# Config variables
config = load_config()

# OpenAI client
client = OpenAI()

# Sidebar
st.sidebar.header(config["streamlit_app"]["sidebar_title"])

# Query to sum up prompt_tokens and completion_tokens separately
sql_query = """
SELECT SUM(prompt_tokens) AS total_prompt_tokens,
       SUM(completion_tokens) AS total_completion_tokens
FROM usage;
"""

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


st.title(config["streamlit_app"]["title"])

# textbox with text "Please enter your question" with "submit" button next to it
question = st.text_input("Please enter your question")

submit = st.button("Submit")

if submit:
    conn, cursor = create_conn_and_cursor()

    system_message = config["gpt"]["system_message"]

    user_message = config["gpt"]["user_message"].replace("{{question}}", question)

    # OpenAI Api ref: https://platform.openai.com/docs/api-reference/chat?lang=python
    model = config["gpt"]["model"]

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    with st.spinner("Please wait, the AI is thinking..."):
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )

    answer = response.choices[0].message.content

    prompt_tokens, completion_tokens = response.usage.prompt_tokens, response.usage.completion_tokens

    # add token usage to datablase
    # 1. Get current datetime as UTC timestamp in milliseconds
    add_token_usage_to_db(conn, cursor, prompt_tokens, completion_tokens)

    # Pattern to match text between `sql\n` and closing ```
    pattern = r"```sql\n(.*?)\n```"
    # Using re.DOTALL to make . match newlines as well
    match = re.search(pattern, answer, re.DOTALL)

    if match:
        this_query = match.group(1)
        
        # Execute the query
        replay = cursor.execute(this_query)

        # print replay rowwise using st.write
        for row in replay:
            st.write(row)

        with st.expander("SQL Query"):
            st.write(this_query)
    else:
        st.write("Errpr-")

    

    conn.close()