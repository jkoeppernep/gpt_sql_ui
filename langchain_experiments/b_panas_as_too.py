"""
b_panas_as_too.py
2024-03-03, JK
LangChain tools, see https://python.langchain.com/docs/use_cases/tool_use/quickstart
"""
from langchain_core.tools import tool
from langchain_openai.chat_models import ChatOpenAI
from langchain.output_parsers import JsonOutputToolsParser
from langchain.output_parsers import JsonOutputKeyToolsParser
from operator import itemgetter


@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int




print(multiply.name)
print(multiply.description)
print(multiply.args)
print(multiply.invoke({"first_int": 4, "second_int": 5}))


model = ChatOpenAI(model="gpt-3.5-turbo-1106")

model_with_tools = model.bind_tools([multiply], tool_choice="multiply")

chain_0 = model_with_tools | JsonOutputToolsParser()

chain_0.invoke("What's four times 23")

chain_1 = model_with_tools | JsonOutputKeyToolsParser(
    key_name="multiply", return_single=True
)

chain_1.invoke("What's four times 23")

chain = (
    model_with_tools
    | JsonOutputKeyToolsParser(key_name="multiply", return_single=True)
    | (lambda input_list: multiply(input_list[0]))
)

chain.invoke("What's four times five")


