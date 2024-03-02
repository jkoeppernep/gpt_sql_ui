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

from utilities import load_config, create_conn_and_cursor


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

st.title(config["streamlit_app"]["title"])

# textbox with text "Please enter your question" with "submit" button next to it
question = st.text_input("Please enter your question")

submit = st.button("Submit")

if submit:
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

    # Pattern to match text between `sql\n` and closing ```
    pattern = r"```sql\n(.*?)\n```"
    # Using re.DOTALL to make . match newlines as well
    match = re.search(pattern, answer, re.DOTALL)

    if match:
        this_query = match.group(1)
        
        st.write(this_query)
    else:
        st.write("Errpr-")

    conn, cursor = create_conn_and_cursor()

    # Execute the query
    replay = cursor.execute(this_query)

    # print replay rowwise using st.write
    for row in replay:
        st.write(row)

    conn.close()