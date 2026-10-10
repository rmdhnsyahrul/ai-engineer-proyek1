import os
from collections.abc import AsyncGenerator
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openrouter import ChatOpenRouter

load_dotenv()

MAX_AGENT_ITERATIONS = 5


@tool
def analyze_csv(file_path: str) -> str:
    """Analyze a CSV file and return descriptive statistics for its columns."""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    try:
        dataframe = pd.read_csv(file_path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        return f"Unable to read CSV file: {exc}"

    return dataframe.describe(include="all").to_string()


tools = [analyze_csv]
tools_by_name = {available_tool.name: available_tool for available_tool in tools}

model = ChatOpenRouter(
    model=os.getenv("AGENT_MODEL", "openrouter/free"),
    temperature=0,
    max_tokens=1024,
    max_retries=2,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_API_BASE"),
)
model_with_tools = model.bind_tools(tools)


def _text_from_content(content: Any) -> str:
    """Extract text from either plain text or LangChain content blocks."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                text_parts.append(block["text"])
        return "".join(text_parts)

    return ""


async def run_agent_events(
    prompt: str,
    max_iterations: int = MAX_AGENT_ITERATIONS,
) -> AsyncGenerator[dict[str, Any], None]:
    """Run the tool-calling agent and yield observable progress events."""
    messages: list[Any] = [{"role": "user", "content": prompt}]

    try:
        for iteration in range(1, max_iterations + 1):
            accumulated_chunk = None

            async for chunk in model_with_tools.astream(messages):
                accumulated_chunk = (
                    chunk
                    if accumulated_chunk is None
                    else accumulated_chunk + chunk
                )

                content = _text_from_content(chunk.content)
                if content:
                    yield {"type": "token", "content": content}

            if accumulated_chunk is None:
                raise RuntimeError("The model returned an empty response.")

            assistant_message = AIMessage(
                content=accumulated_chunk.content,
                tool_calls=accumulated_chunk.tool_calls,
            )
            messages.append(assistant_message)

            if not assistant_message.tool_calls:
                yield {"type": "done", "iterations": iteration}
                return

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call["name"]
                selected_tool = tools_by_name.get(tool_name)
                if selected_tool is None:
                    raise ValueError(f"Unknown tool requested by model: {tool_name}")

                yield {
                    "type": "tool_call",
                    "name": tool_name,
                    "args": tool_call["args"],
                }

                result = await selected_tool.ainvoke(tool_call["args"])
                result_text = str(result)
                messages.append(
                    ToolMessage(
                        content=result_text,
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                    )
                )
                yield {
                    "type": "tool_result",
                    "name": tool_name,
                    "content": result_text,
                }

        yield {
            "type": "error",
            "error": f"Agent exceeded the maximum of {max_iterations} iterations.",
        }
    except Exception as exc:
        yield {"type": "error", "error": str(exc)}