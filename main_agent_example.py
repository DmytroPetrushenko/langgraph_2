from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain.schema import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain.agents import AgentExecutor, AgentType, Tool
from langchain.agents.agent_toolkits import create_openai_fn_agent
from langchain.agents import AgentType, load_tools

from typing import Optional, List, Any

import forge
import utils.orm_util as orm
from tools.msf_tools import get_msf_sub_groups_list, get_msf_exact_sub_group_modules_list
from workflows.graph_entities.statets import TeamState


def assistant_agent_with_constructed_output(
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
        An agent executor_exp configured to produce structured outputs and capable of using tools.
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

    # If tools are provided, create an agent that can use them
    if tools:
        # Create the agent using the AgentExecutor
        agent = create_openai_fn_agent(
            llm=llm_chain,
            tools=tools,
            verbose=True
        )
        return agent
    else:
        # Return the chain without tools
        return llm_chain


model_gpt = forge.create_llm(model_name='gpt-4o')
# planner_system_message = orm.create_message_from_file("planning_team/operation_planner#2.txt")
# PLANNING_TOOLS = [
#     get_msf_sub_groups_list,
#     get_msf_exact_sub_group_modules_list
# ]
#
#
# agent = assistant_agent_with_constructed_output(
#     model_llm=model_gpt,
#     system_message=planner_system_message,
#     tools=PLANNING_TOOLS
# )
#
# print(agent)


