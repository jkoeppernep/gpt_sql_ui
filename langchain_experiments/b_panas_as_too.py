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
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent


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

invoke_chain = False

if invoke_chain:
    print(chain.invoke("What's four times the number of days in January?"))

## Agent for colling the tool multiple times depending on the input
# Prompt
prompt = hub.pull("hwchase17/openai-tools-agent")

print(
    prompt.messages
)

# [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], 
# template='You are a helpful assistant')), MessagesPlaceholder(variable_name='chat_history', optional=True), HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')), 
# MessagesPlaceholder(variable_name='agent_scratchpad')]

# Tools
@tool
def add(first_int: int, second_int: int) -> int:
    "Add two integers."
    return first_int + second_int


@tool
def exponentiate(base: int, exponent: int) -> int:
    "Exponentiate the base to the exponent power."
    return base**exponent


tools = [multiply, add, exponentiate]

# Only certain models support this
model = ChatOpenAI(
    model="gpt-3.5-turbo-1106", 
    temperature=0,
    verbose=True
)

# Construct the OpenAI Tools agent
agent = create_openai_tools_agent(model, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# set more debug output
from langchain.globals import set_debug
set_debug(False)

execute_agent = False

if execute_agent:
    print(
        agent_executor.invoke(
            {
                "input": "Take 3 to the fifth power and multiply that by the sum of twelve and three, then square the whole result"
            }
        )
    )


## Simple agent to unsertand its working
# Tools: multiply, print
# Task: print a*b on console


@tool
def print_result(result: int):
    """Print the result to the console."""

    print(result)

print_prompt = hub.pull("hwchase17/openai-tools-agent")

print_tools = [multiply, print_result]

print_model = ChatOpenAI(
    model="gpt-3.5-turbo-1106", 
    temperature=0,
    verbose=True
)

print_agent = create_openai_tools_agent(
    print_model, 
    print_tools, 
    print_prompt,
)

print_agent_executor = AgentExecutor(
    agent=print_agent, 
    tools=print_tools, 
    verbose=True
)

execute_print_agent = True

if execute_print_agent:
    print(f"print_agent_executor {'-'*20}")

    print_agent_executor.invoke(
        {
            "input": "Print 3 times 5 on console."
        }
    )

# Next: debug https://kleiber.me/blog/2023/05/14/tracking-inspecting-prompts-langchain-agents-weights-and-biases/

