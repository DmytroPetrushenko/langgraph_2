from typing import Sequence, Union, Callable, Any, Dict, List

from langchain.schema import HumanMessage, AIMessage
from langchain_core.messages import ToolMessage, BaseMessage
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
    return {MESSAGES_FIELD: tool_messages}


def create_ordinary_node(state: TeamState | PlanningTeamState, agent, name: str):
    """
    Creates a standard node by invoking an agent with the current state and returning the updated state.

    Args:
        state: The current state (PlanningState or UnifiedState), containing messages and sender information.
        agent: The agent to invoke using the messages from the state.
        name: The name of the node or agent invoking the operation.

    Returns:
        A dictionary containing the updated messages and sender after invoking the agent.
    """
    messages: List[BaseMessage] = state.messages
    last_senders  = state.sender[-1]
    task_message = messages[0]
    if name is PLAN_COMPOSITION_NODE and last_senders is MODULE_EXTRACTION_NODE:
        messages = [messages[0], HumanMessage(content=f"The relevant modules: {state.modules}")]
    if name is PLAN_COMPOSITION_NODE and last_senders is VALIDATOR_EXTRACTION_NODE:
        messages = [
            HumanMessage(
                content=f"Please improve the previously created plan:\n<<\n{state.plan}\n>>\n"
                        f"based on the feedback from the Validator Agent:\n<<\n{state.validator_feedback}\n>>.\n"
                        f"If no improvements are needed, add 'FINAL ANSWER' at the end of your message."
            )
        ]
    if name is PLAN_VALIDATOR_NODE:
        messages = [
            HumanMessage(
                content=f"Please review the following pentesting plan using the Metasploit Framework:\n<<\n{state.plan}"
                        f"\n>>\nand evaluate its alignment with the task:\n\"{task_message.content}\"\n"
                        f"Focus on identifying any gaps or inefficiencies and suggest improvements for automated "
                        f"testing."
)]
    # Invoke the agent with the current state
    response = agent.invoke(messages)

    # Return the updated state, which includes the new message and sender's name
    return {
        MESSAGES_FIELD: [response],  # Add the new message to the list of messages
        SENDER_FIELD: [name]  # Set the sender to the current agent's name
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
        MESSAGES_FIELD: [
            HumanMessage(content=message_from_host)  # Forward the last message content
        ],
        SENDER_FIELD: state.sender,  # Retain the original sender information
        PLAN_FIELD: state.plan
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
        MESSAGES_FIELD: [
            HumanMessage(content=cleaned_content)  # Set the cleaned content without "FINAL ANSWER"
        ],
        SENDER_FIELD: node_name,  # Set the sender to the specified node name
        PLAN_FIELD: cleaned_plan
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
        MESSAGES_FIELD: [human_message],  # Add the response message to the list of messages
        SENDER_FIELD: name
    }


def create_extraction_script_node(state: PlanningTeamState, name: str):
    typical_sub_group_message = 'The list of sub_groups was added to "sub_groups" field in PlanningTeamState!'
    typical_modules_message = 'The list of modules was added to "modules" field in PlanningTeamState!'
    sub_groups: List[str] = []
    modules: List[str] = []

    for message in state.messages:
        if message.content not in [typical_modules_message, typical_sub_group_message]:
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
        MESSAGES_FIELD: state.messages,
        SENDER_FIELD: name,
        SUB_GROUPS_FIELD: sub_groups,
        MODULES_FIELD: modules
    }


def create_module_extraction_node(state: TeamState, agent, name: str):
    """
    Creates a module extraction node based on the last message sender in the team's state.

    This function invokes the given agent with the latest message from the team's state and
    determines what information needs to be extracted (module subgroups, modules, or the plan)
    based on the sender of the last message. Depending on the sender, it creates the appropriate
    output for updating the team's state.

    Args:
        state (TeamState): The current state of the team, which includes the list of messages and senders.
        agent: The agent responsible for processing the latest message and returning relevant information.
        name (str): The name of the current module extraction node, which will be added to the sender field.

    Returns:
        dict: A dictionary containing the updated fields (messages, sender, and either subgroups, modules, or the plan)
              based on the last sender in the state.

    Raises:
        ValueError: If the last sender is not recognized as one of the expected nodes: MODULE_GROUP_SELECTION_NODE,
                    MODULE_SELECTION_NODE, or PLAN_COMPOSITION_NODE.
    """

    # Get the agent's response to the last message in the team's state
    response: Dict[str, List[str]] = agent.invoke([state.messages[-1]])
    last_sender = state.sender[-1]  # Retrieve the last sender from the team's state

    # Check the last sender and update the appropriate fields based on its value
    if last_sender is MODULE_GROUP_SELECTION_NODE:
        output = {
            MESSAGES_FIELD: [AIMessage(content=SUB_GROUPS_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            SUB_GROUPS_FIELD: response.get(SUB_GROUPS_FIELD)
        }
    elif last_sender is MODULE_SELECTION_NODE:
        output = {
            MESSAGES_FIELD: [AIMessage(content=MODULES_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            MODULES_FIELD: response.get(MODULES_FIELD)
        }
    elif last_sender is PLAN_COMPOSITION_NODE:
        output = {
            MESSAGES_FIELD: [AIMessage(content=PLAN_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            PLAN_FIELD: response.get(PLAN_FIELD)
        }
    elif last_sender is PLAN_VALIDATOR_NODE:
        output = {
            MESSAGES_FIELD: [AIMessage(content=VALIDATOR_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            VALIDATOR_FIELD: response.get(VALIDATOR_FIELD)
        }
    else:
        # Raise an error if the sender is not one of the expected nodes
        raise ValueError(f"Unexpected sender: '{last_sender}' in {name}. "
                         f"Expected -> {MODULE_GROUP_SELECTION_NODE} or {MODULE_SELECTION_NODE} or "
                         f"{PLAN_COMPOSITION_NODE}.")

    # Return the constructed output dictionary for updating the team's state
    return output

