"""
langchain_cat.py
2024-03-03, JK

This app is a console based chatbot using LangChain an OpenAI GPT-3 model.

LangChain documentation: https://python.langchain.com/docs/get_started/quickstart
"""
import re
from typing import List

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ------------------------------
## Functions
# ------------------------------
def extract_text_within_backticks(text):
    pattern = r"```(.*?)```"

    result = re.findall(pattern, text)

    return result

# ------------------------------
## App
# ------------------------------
json_sql_prompt = ChatPromptTemplate.from_messages([
    ("system", "You reply with as few words as possible. If you don't know the answer, just say 'I don't know'."),
    ("user", "What's the capital of {input}")
])

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo-0125"
)

chain_prompt_llm = json_sql_prompt | llm 

for this_countriy in ["Germany", "France", "Johannestan"]:
    print(
        chain_prompt_llm.invoke({"input": f"{this_countriy}"})
    )

# Output parser
output_parser = StrOutputParser()

chain_prompt_llm_parser = json_sql_prompt | llm | output_parser

for this_countriy in ["Germany", "France", "Johannestan"]:
    print(
        chain_prompt_llm_parser.invoke({"input": f"{this_countriy}"})
    )


# ------------------------------
## SQL chain
# ------------------------------
sql_system_message = """
You're an expert in writing SWL queries. You reply with as few words as possible. If you don't know the answer, just say 'I don't know.
You only provide the SQL query, not the result. You anwer with nothing more then the query.
You encaplulate the query in three backticks, like this: ```SELECT * FROM table```\n
The table is named table. It got the columns id, name, and age. The id is an integer, the name is a string, and the age is an integer.
""".strip()

sql_user_message = """
Give the SQL query to: {task}
"""

sql_prompt = ChatPromptTemplate.from_messages([
    ("system", sql_system_message),
    ("user", sql_user_message)
])

sql_output_parser = StrOutputParser()

sql_chain = sql_prompt | llm | sql_output_parser

tasks = [
    "Get number of rows in my table",
]

for this_task in tasks:
    print(
        sql_chain.invoke({"task": f"{this_task}"})
    )





# Define your desired data structure.
class SqlQuery(BaseModel):
    sql_query: str = Field(description="the SQL query to execute")


# Set up a parser + inject instructions into the prompt template.
parser = JsonOutputParser(pydantic_object=SqlQuery)

json_sql_prompt = PromptTemplate(
    template="In my SQL database is table called 'table' with columns id, name, and age. The id is an integer, the name is a string, and the age is an integer. Give the SQL query to answer my question.\n{format_instructions}\n{task}\n",
    input_variables=["task"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = json_sql_prompt | llm | parser

answers = []

for this_task in tasks:
    print(
        this_answer := chain.invoke({"task": f"{this_task}"})
    )

    answers.append(this_answer)



