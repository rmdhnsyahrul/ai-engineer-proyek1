import getpass
import os
import pandas as pd
from langchain_core.tools import tool

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# 1. Tools: Define the tools that the agent can use. In this case, we have a tool to analyze CSV files.
@tool
def analyze_csv(file_path: str) -> str:
    """
    Analyze a CSV file and return a summary of its contents.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        str: A summary of the CSV file's contents.
    """
    if not os.path.exists(file_path):
        return "File not found."

    df = pd.read_csv(file_path)
    summary = df.describe().to_string()
    return summary

# 2. Tools list: Create a list of tools that the agent can use.
tools = [analyze_csv]
tools_by_name = {tool.name: tool for tool in tools}

# 3. Initialize LLM: Initialize the language model that the agent will use to process natural language queries.
from langchain_openrouter import ChatOpenRouter
model = ChatOpenRouter(
    model="openrouter/free",
    temperature=0,
    max_tokens=1024,
    max_retries=2,
    # other params...
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_API_BASE")
)

model_with_tools = model.bind_tools(tools)

if __name__ == "__main__":
    # Example usage: Analyze a CSV file and get a summary.
    file_path = "data/transaksi_pengadaan.csv"  # Replace with your CSV file path
    messages = [{
        "role": "user",
        "content": f"Analyze the CSV file at {file_path}"
    }]

    result = model_with_tools.invoke(messages)
    messages.append(result)

    for tool_call in result.tool_calls:
        # Execute the tool with the generated arguments
        print(f"Tool call: {tool_call['name']} with arguments {tool_call['args']}")
        tool = tools_by_name[tool_call["name"]]

        print(f"Invoking tool: {tool.name} with arguments {tool_call['args']}")
        tool_result = tool.invoke(tool_call)

        print(f"Tool result: {tool_result}")
        messages.append(tool_result)

    # Step 3: Pass results back to model for final response
    final_response = model_with_tools.invoke(messages)
    print(final_response.text)
