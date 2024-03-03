"""
a_answer_as_json.py
2024-03-03, JK
Ask GPT to give a name spli into first and last name. Reply as JSON.
"""
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
import pandas as pd 


# LLM
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo-0125",
    temperature=0.9,
)

# Define a class for the name to specify the format of the JSON response
class Name(BaseModel):
    first_name: str = Field(description="First name like John")
    last_name: str = Field(description="last name like Doe")

# Output parser
parser = JsonOutputParser(pydantic_object=Name)

# Prompt
prompt = PromptTemplate(
    template="Please think of a typical {region} name comprising of a first and last name\n{format_instructions}",
    input_variables=["region"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


chain = prompt | llm | parser

if __name__ == "__main__":
    res_list = []

    for this_country in ["German", "French", "Italian"]:
        res = chain.invoke({"region": this_country})

        res_list.append(res)
    
    # Print tres
    df = pd.DataFrame(res_list)

    print(df)


