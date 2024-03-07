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
import ast

from utilities import load_config, create_conn_and_cursor, add_token_usage_to_db, display_token_usage_in_sidebar, copy_db


# ------------------------------
## Parameters
# ------------------------------
parameters = {
    "use_function_calling": True,
}

# ------------------------------
## Sesstion states
# ------------------------------
# Check if db_copied exists in sesston state, if not, create it
if "db_copied" not in st.session_state:
    copy_db()

    st.session_state.db_copied = True

# ------------------------------
## Application
# ------------------------------
# Config variables
config = load_config()

# OpenAI client
client = OpenAI()

# Sidebar
st.sidebar.header(config["streamlit_app"]["sidebar_title"])

display_token_usage_in_sidebar()


st.title(config["streamlit_app"]["title"])

# textbox with text "Please enter your question" with "submit" button next to it
question = st.text_input("Please enter your question")

submit = st.button("Submit")

if submit:
    conn, cursor = create_conn_and_cursor()

    # OpenAI Api ref: https://platform.openai.com/docs/api-reference/chat?lang=python
    model = config["gpt"]["model"]

    if not parameters["use_function_calling"]:
        with st.spinner("Please wait, the AI is thinking..."):
            system_message = config["gpt"]["system_message"]

            user_message = config["gpt"]["user_message"].format(question=question)

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "Answer: "},
            ]

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )

        this_query = response.choices[0].message.content

        st.write(this_query)

        prompt_tokens, completion_tokens = response.usage.prompt_tokens, response.usage.completion_tokens

        # add token usage to datablase
        # 1. Get current datetime as UTC timestamp in milliseconds
        add_token_usage_to_db(conn, cursor, prompt_tokens, completion_tokens)
    else:
        # See docu ai https://platform.openai.com/docs/guides/function-calling
        
        with st.spinner("Please wait, the AI is thinking..."):
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "cursor_execute",
                        "description": "Executes a SQL query on a database and returns the result.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "operation": {
                                    "type": "string",
                                    "description": "A string that contains a SQL query. The function is offered by sqlite3.connect().cursor()",
                                }
                            },
                            "required": ["operation"],
                        },
                    },
                }
            ]

            system_message = config["gpt"]["system_message_fun_calling"]

            user_message = config["gpt"]["user_message_fun_calling"].format(question=question)

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ]

            response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages,
                tools=tools,
                tool_choice="auto",  # auto is default, but we'll be explicit
            )

        this_query = ast.literal_eval(response.choices[0].message.tool_calls[0].function.arguments)["operation"]

    # Remove the ``` from the answer
    # this_query = answer.rstrip("```")

    # Execute the query
    replay = cursor.execute(this_query)

    # print replay rowwise using st.write
    for row in replay:
        st.markdown(row)

    with st.expander("SQL Query"):
        st.write(this_query)

    conn.close()
