from typing import Sequence, Union, Callable, Any, Dict, List

from langchain.schema import HumanMessage, AIMessage
from langchain_community.chat_models import ChatAnthropic
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import ToolInvocation, ToolExecutor

from constants import *
from workflows.graph_entities.statets import TeamState, PlanningTeamState
from workflows.team_pentest.graph_handlers.graph_executor import launch_as_subgraph


def create_tool_node(state, tools: Sequence[Union[BaseTool, Callable]]) -> Dict[str, List[ToolMessage]]:
    messages = state.messages

    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    # We construct an ToolInvocation from the function_call
    tool_calls = last_message.tool_calls
    tool_messages = []
    for tool_call in tool_calls:
        action = ToolInvocation(
            tool=tool_call["name"],
            tool_input=tool_call["args"]
        )
        tool_executor = ToolExecutor(tools)
        # We call the tool_executor and get back a response
        response = tool_executor.invoke(action)
        # We use the response to create a ToolMessage
        tool_message = ToolMessage(
            content=str(response),
            name=action.tool,
            tool_call_id=tool_call["id"]
        )
        tool_messages.append(tool_message)
    # We return a list, because this will get added to the existing list
    return {"messages": tool_messages}


def create_ordinary_node(state: TeamState, agent, name: str):
    """
    Creates a standard node by invoking an agent with the current state and returning the updated state.

    Args:
        state: The current state (PlanningState or UnifiedState), containing messages and sender information.
        agent: The agent to invoke using the messages from the state.
        name: The name of the node or agent invoking the operation.

    Returns:
        A dictionary containing the updated messages and sender after invoking the agent.
    """

    # Invoke the agent with the current state
    response = agent.invoke(state.messages)

    # Return the updated state, which includes the new message and sender's name
    return {
        "messages": [response],  # Add the new message to the list of messages
        "sender": name  # Set the sender to the current agent's name
    }


def create_node_with_construct_output(state: TeamState, agent, name: str):
    """
    Creates a standard node by invoking an agent with the current state and returning the updated state.

    Args:
        state: The current state (PlanningState or UnifiedState), containing messages and sender information.
        agent: The agent to invoke using the messages from the state.
        name: The name of the node or agent invoking the operation.

    Returns:
        A dictionary containing the updated messages and sender after invoking the agent.
    """
    # Invoke the agent with the current state
    response = agent.invoke(state.messages)

    # Return the updated state, which includes the new message and sender's name
    return {
        "messages": [AIMessage(content=response['message'])],  # Add the new message to the list of messages
        "sender": name,  # Set the sender to the current agent's name
        "plan": response['plan']
    }


def node_connector_to_other_team(state, compiled_graph, node_name: str, thread_id: int):
    """
    Connects the current team lead node to another team's graph and forwards the message.

    Args:
        state: The current state, containing messages and sender information.
        compiled_graph: The compiled graph of the other team (e.g., the planning team).
        node_name: The name of the node to which the message should be forwarded.
        thread_id: The thread identifier used for the execution configuration.

    Returns:
        A dictionary representing the updated state with the response from the node of the other team.
    """
    message_from_host = state.messages[-1].content
    if node_name is TESTING_NODE:
        message_from_host += f"\n{state.plan}"

    # Prepare input from the team lead to be forwarded to the other team (e.g., planning team)
    input_from_team_lead: Dict[str, Any] = {
        "messages": [
            HumanMessage(content=message_from_host)  # Forward the last message content
        ],
        'sender': state.sender,  # Retain the original sender information
        'plan': state.plan
    }

    # Launch the subgraph of the other team (e.g., planning team) using the forwarded message
    state_executed_graph: TeamState = launch_as_subgraph(
        compiled_graph=compiled_graph,
        inputs=input_from_team_lead,
        thread_id=thread_id
    )

    # Get the content from the last message of the executed graph
    content = state_executed_graph['messages'][-1].content

    # Get the plan from the state of the executed graph
    plan: str = state_executed_graph['plan']
    cleaned_plan = plan.replace(FINAL_ANSWER, "").strip()

    # Remove "FINAL ANSWER" from the content if it exists
    cleaned_content = content.replace(FINAL_ANSWER, "").strip()

    if node_name is PLANNER_NODE:
        cleaned_content = "Creating the detailed pentest plan. It was saved in Graph State Field -> \"plan\"!"

    # Return the updated state with the cleaned response from the other team
    return {
        "messages": [
            HumanMessage(content=cleaned_content)  # Set the cleaned content without "FINAL ANSWER"
        ],
        'sender': node_name,  # Set the sender to the specified node name
        'plan': cleaned_plan
    }


def create_quasi_human_node(state: TeamState, name: str) -> dict:
    """
    Creates a quasi-human node by invoking an agent with the current state and returning the updated state.

    Args:
        state (SubgraphState | UnifiedState): The current state (SubgraphState or UnifiedState),
                                              containing messages and sender information.

        name (str): The name of the node or agent invoking the operation.

    Returns:
        dict: A dictionary containing the updated messages after invoking the agent.
    """
    # Update the state with a predefined human-like message
    if PLANNER_NODE in state.sender:
        human_message = HumanMessage(
            content="You forgot to include who you're addressing your message! Add \"TASK RUNER\" to your message!"
        )
    else:
        human_message = HumanMessage(
            content="Hi there! It seems your response is incomplete—you didn't include 'FINAL "
                    "ANSWER' at the end. Could you please finish your message accordingly?"
        )

    # Return the updated state with the response from the agent
    return {
        "messages": [human_message],  # Add the response message to the list of messages
        "sender": name
    }


def create_extraction_node(state: PlanningTeamState, name: str):
    typical_sub_group_message = 'The list of sub_groups was added to "sub_groups" field in PlanningTeamState!'
    typical_modules_message = 'The list of modules was added to "modules" field in PlanningTeamState!'
    sub_groups: List[str] = []
    modules: List[str] = []

    for message in state.messages:
        if not message.content in [typical_modules_message, typical_sub_group_message]:
            # If the message is related to module group selection
            if MODULE_GROUP_SELECTION_NODE == message.name:
                sub_groups.append(message.content)
                message.content = typical_sub_group_message
            # If the message is related to module selection
            elif MODULE_SELECTION_NODE == message.name:
                modules.append(message.content)
                message.content = typical_modules_message
            # Ignore other messages
            else:
                # Skip unrelated messages without raising an exception
                continue

            # Check if neither sub_groups nor modules were added
    if not sub_groups and not modules:
        raise Exception('No valid sub_groups or modules found in the messages!')

    # Return the result with updated messages, sender, sub_groups, and modules
    return {
        'messages': state.messages,
        'sender': name,
        'sub_groups': sub_groups,
        'modules': modules
    }

