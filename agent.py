import os
import asyncio
from typing import Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
import re
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into environment

llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-2.0-flash",
    max_output_tokens=2048,
    temperature=0.2,
)


tool_usage_log = []
stored_numbers = {"values": []}

def log_tool_usage(tool_name: str, input_data: Any):
    """Logs the tool used and its input."""
    tool_usage_log.append({"tool": tool_name, "input": input_data})

@tool
def extract_numbers(text: str) -> str:
    """Extracts all numbers from the input text and stores them in memory."""
    log_tool_usage("extract_numbers", text)
    numbers = [int(num) for num in re.findall(r'\d+', text)]
    if numbers:
        stored_numbers["values"].extend(numbers)
        return f"Extracted and stored numbers: {numbers}"
    else:
        return "No numbers found in the input."

@tool
def calculate_average_stored(_: str = "") -> str:
    """Calculates the average of all stored numbers."""
    log_tool_usage("calculate_average_stored", _)
    if not stored_numbers["values"]:
        return "No numbers stored yet."
    avg = sum(stored_numbers["values"]) / len(stored_numbers["values"])
    return f"The average of stored numbers is {avg}"

@tool
def compare_with_average(number: str) -> str:
    """Compares the given number with the average of stored numbers."""
    log_tool_usage("compare_with_average", number)
    if not stored_numbers["values"]:
        return "No numbers stored yet."
    try:
        avg = sum(stored_numbers["values"]) / len(stored_numbers["values"])
        num = float(number)
        if num > avg:
            return f"{num} is greater than the average ({avg})"
        elif num < avg:
            return f"{num} is less than the average ({avg})"
        else:
            return f"{num} is equal to the average ({avg})"
    except Exception as e:
        return f"Error: {str(e)}"

tools = [extract_numbers, calculate_average_stored, compare_with_average]
llm_with_tools = llm.bind_tools(tools)

MEMORY_KEY = "chat_history"

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a powerful assistant, but bad at extracting numbers, calculating averages, and comparing numbers.",
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

async def main():
    chat_history = []
    while True:
        print("Enter question or type exit to quit")
        input1 = input("User: ")

        if input1.lower() == "exit":
            print("Exiting the chat.")
            break

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: agent_executor.invoke({"input":input1 , "chat_history": chat_history}))

        chat_history.extend(
        [
            HumanMessage(content=input1),
            AIMessage(content=result["output"]),
        ]
    )
        print("\nTools Used:")
        for usage in tool_usage_log:
            print(f"Tool: {usage['tool']}, Input: {usage['input']}")
            
        print("\n\n Message:\n", result["output"])

if __name__ == "__main__":
    asyncio.run(main())