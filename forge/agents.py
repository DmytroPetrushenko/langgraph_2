import os
from typing import List, Optional, Union, Any
from pathlib import Path

from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langsmith import Client

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

import constants
import utils


def create_agent(agent_name: str, prompts: ChatPromptTemplate, llm_with_tools):
    agent = (
            {
                "input": lambda x: x["input"],
                agent_name: lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompts
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
    )

    return agent


def create_executor(llm, tools):
    # Get the prompt to use - you can modify this!
    prompt = Client().pull_prompt("wfh/react-agent-executor")
    prompt.pretty_print()

    # return agent executor
    return create_react_agent(llm, tools, state_modifier=prompt)


def create_agent_v2(
        llm: Any,
        system_message: Union[str, Path],
        tools: Optional[List] = None,
        default_message: Union[str, Path] = constants.DEFAULT_MESSAGE
) -> Any:
    """
    Create an agent with the specified language model, system message, and tools.

    Args:
        llm (Any): The language model to use.
        system_message (Union[str, Path]): The system message or path to the system message file.
        tools (Optional[List]): List of tools available to the agent.
        default_message (Union[str, Path]): The default message or path to the default message file.

    Returns:
        Any: The created agent.

    Raises:
        ValueError: If a specified message file cannot be found.
    """
    try:
        # Load system message
        if isinstance(system_message, (str, Path)) and os.path.isfile(str(system_message)):
            system_message_content = utils.create_message_from_file(system_message)
        else:
            system_message_content = str(system_message)

        # Load default message
        if isinstance(default_message, (str, Path)) and os.path.isfile(str(default_message)):
            default_message_content = utils.create_message_from_file(default_message)
        else:
            default_message_content = str(default_message)

    except FileNotFoundError as e:
        raise ValueError(f"Cannot find message file: {e.filename}")

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_message_content),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # Apply the system message
    prompt = prompt.partial(system_message=system_message_content)

    # Add tool names if tools are provided
    if tools:
        tool_names = ", ".join(tool.__name__ for tool in tools)
        prompt = prompt.partial(tool_names=tool_names)

    # Bind the tools to the language model
    return prompt | llm.bind_tools(tools or [])
