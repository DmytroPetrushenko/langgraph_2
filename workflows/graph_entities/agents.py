from typing import List, Optional, Any

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import create_structured_chat_agent

import utils

from utils import orm_util as orm
from workflows.graph_entities.statets import TeamState


def assistant_agent_with_tools(model_llm: ChatOpenAI | ChatAnthropic, tools, system_message: str):
    """
    Create an agent with specified tools and a system message.

    Args:
        model_llm: The agent model to bind tools with.
        tools: A list of tools to integrate into the agent.
        system_message: A specialized system message to customize the agent's behavior.

    Returns:
        A configured prompt bound with the model and tools.
    """
    # Ensure tools is a valid list
    if not tools or not isinstance(tools, list):
        raise ValueError("Invalid tools input. Must be a non-empty list of tools.")

    # Load the default template message for the system
    default_with_tool = utils.orm_util.create_message_from_file('default_with_tool.txt')

    # Define the prompt template using the system message and placeholder for dynamic messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_with_tool),
            (MessagesPlaceholder(variable_name="messages"))
        ]
    )

    # Partially specialize the prompt with the provided system message
    prompt = prompt.partial(system_message=system_message)

    # Add tool names to the prompt by joining their names into a string
    tool_names = ", ".join(tool.name for tool in tools)
    if not tool_names:
        raise ValueError("Tool names are missing or empty.")

    prompt = prompt.partial(tool_names=tool_names)

    # Bind the tools to the model and return the configured prompt
    return prompt | model_llm.bind_tools(tools)


def assistant_agent_without_tools(
        model_llm: ChatOpenAI | ChatAnthropic,
        system_message: str
):
    """
    Create an agent without tools, customized with a system message.

    Args:
        model_llm: The agent model to configure.
        system_message: A system message that adds specific instructions or context to the agent.
        teams: An optional list of team names that will be passed to the agent.

    Returns:
        A prompt configured with the model and system message.
    """
    # Load the default template message for agents without tools
    default_without_tools = orm.create_message_from_file('default_without_tools.txt')

    # Validate system_message input
    if not system_message or not isinstance(system_message, str):
        raise ValueError("Invalid system message. It must be a non-empty string.")

    # Define the prompt template with system message and placeholder for dynamic messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_without_tools),
            (MessagesPlaceholder(variable_name="messages"))
        ]
    )

    # Add specialization to the current agent using the system message and teams (if provided)
    prompt = prompt.partial(system_message=system_message)

    # Bind the prompt to the model and return it
    return prompt | model_llm


def assistant_agent_with_constructed_output(
        model_llm: ChatOpenAI | ChatAnthropic,
        system_message: str,
        oai_schema,
        teams: Optional[List[str]] = None
):
    """
    Create an agent with a specified system message and return the prompt bound with the model,
    configured to handle structured output.

    Args:
        model_llm: The agent model (ChatOpenAI or ChatAnthropic) to bind the prompt with.
        system_message: A specialized system message to customize the agent's behavior.
        teams: An optional list of team names that will be passed to the agent.
        oai_schema: ddd
    Returns:
        A configured prompt bound with the model and structured output (TeamState).

    """

    # Load the default template message for agents without tools
    default_without_tools = orm.create_message_from_file('default_without_tools.txt')

    # Validate system_message input
    if not system_message or not isinstance(system_message, str):
        raise ValueError("Invalid system message. It must be a non-empty string.")

    # Define the prompt template using the system message and placeholder for dynamic messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_without_tools),
            (MessagesPlaceholder(variable_name="messages"))
        ]
    )

    # Add specialization to the current agent using the system message and teams (if provided)
    prompt = prompt.partial(system_message=system_message, teams=teams)

    # Bind the structured output (TeamState) and return the configured prompt
    return prompt | model_llm.with_structured_output(
        schema=oai_schema,
        method="json_schema"
    )


def assistant_agent_with_constructed_output_bind_tools(
        model_llm: ChatOpenAI | ChatAnthropic,
        system_message: str,
        teams: Optional[List[str]] = None,
        tools: Optional[List[Any]] = None
):
    """
    Create an agent with a specified system message, bind it with the model,
    configure it to handle structured output, and integrate tools for the agent to use.

    Args:
        model_llm: The agent model (ChatOpenAI or ChatAnthropic) to bind the prompt with.
        system_message: A specialized system message to customize the agent's behavior.
        teams: An optional list of team names that will be passed to the agent.
        tools: An optional list of tools that the agent can use.

    Returns:
        An agent configured to produce structured outputs and capable of using tools.
    """

    # Load the default template message for agents without tools
    default_without_tools = orm.create_message_from_file('default_without_tools.txt')

    # Validate system_message input
    if not system_message or not isinstance(system_message, str):
        raise ValueError("Invalid system message. It must be a non-empty string.")

    # Define the prompt template using the system message and placeholder for dynamic messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_without_tools),
            (MessagesPlaceholder(variable_name="messages"))
        ]
    )

    # Add specialization to the current agent using the system message and teams (if provided)
    prompt = prompt.partial(system_message=system_message, teams=teams)

    # Create the LLM chain with the prompt and model, including structured output
    llm_chain = prompt | model_llm.with_structured_output(TeamState)

    # If tools are provided, initialize an agent that can use them
    if tools:
        agent = create_structured_chat_agent(
            llm=llm_chain,
            tools=tools,
            prompt=prompt
        )
        return agent
    else:
        # Return the chain without tools
        return llm_chain
