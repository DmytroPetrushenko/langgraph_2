import functools
import re
from typing import Literal, Optional, List, Any, Dict
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from constants import PLANNER_NODE, HELPER_TOOLS_NODE
from utils import orm_util as orm
from tools.msf_tools import get_msf_sub_groups_list, get_msf_exact_sub_group_modules_list
from workflows.graph_entities.agents import assistant_agent_with_tools, assistant_agent_with_constructed_output
from workflows.graph_entities.nodes import create_tool_node, create_ordinary_node, \
    create_node_with_construct_output
from workflows.graph_entities.statets import TeamState

# Define constants for the Operation Planner node
TOOL_NODE_NAME = "call_tool"  # Name of the node responsible for handling tool execution
pattern_helper = re.compile(f'{HELPER_TOOLS_NODE}')
pattern_final_answer = re.compile(f"FINAL ANSWER")
PLANNING_TOOLS = [
    get_msf_sub_groups_list,
    get_msf_exact_sub_group_modules_list
]  # List of tools used by the Operation Planner


def create_graph_planning_team_e1(
        model_llm,
        all_sys_messages_paths: Optional[Dict[Literal['helper', 'planner'], str]] = None,
        tools: Optional[List[Any]] = None
):
    # default entities
    default_planner_sys_message_path = "planning_team/operation_planner#3.txt"
    default_helper_sys_message_path = "helper_agent/helper#1.txt"

    # Define the tools to be used by the Operation Planner agent
    tools = PLANNING_TOOLS if tools is None else tools

    # Load system messages to guide the Operation Planner agent
    if all_sys_messages_paths is None:
        all_sys_messages_paths = {}

    helper_sys_message_path = all_sys_messages_paths.get('helper', default_helper_sys_message_path)
    planner_sys_message_path = all_sys_messages_paths.get('planner', default_planner_sys_message_path)

    # Create messages using the ORM
    planner_system_message = orm.create_message_from_file(planner_sys_message_path)
    helper_system_message = orm.create_message_from_file(helper_sys_message_path)

    # Creation Helper agent with tools using the provided system message
    helper_agent = assistant_agent_with_tools(
        model_llm=model_llm,
        tools=tools,
        system_message=helper_system_message
    )

    # Create the Operation Planner agent using the provided tools and system message
    operation_planner_agent = assistant_agent_with_constructed_output(
        model_llm=model_llm,
        system_message=planner_system_message,
        teams=[HELPER_TOOLS_NODE]
    )

    # operation_planner_agent = assistant_agent_with_constructed_output_bind_tools(
    #     model_llm=model_llm,
    #     system_message=planner_system_message,
    #     tools=PLANNING_TOOLS
    # )

    # Define the Operation Planner node that will handle the planning logic
    operation_planner_node = functools.partial(
        create_node_with_construct_output,
        agent=operation_planner_agent,
        name=PLANNER_NODE
    )

    # Define the Helper node that will handle the planning logic
    helper_node = functools.partial(
        create_ordinary_node,
        agent=helper_agent,
        name=HELPER_TOOLS_NODE
    )

    # Define the tool node responsible for executing tools within the graph
    tool_node = functools.partial(
        create_tool_node,
        tools=tools
    )

    # Define the quasi node responsible for re-asking ..
    # qausi_human_node = functools.partial(
    #     create_quasi_human_node,
    #     name=QUASI_HUMAN_NODE
    # )


    # Initialize the state graph with SubgraphState
    workflow = StateGraph(TeamState)

    # Add nodes to the graph
    workflow.add_node(PLANNER_NODE, operation_planner_node)
    workflow.add_node(HELPER_TOOLS_NODE, helper_node)
    workflow.add_node(TOOL_NODE_NAME, tool_node)
    # workflow.add_node(QUASI_HUMAN_NODE, qausi_human_node)

    # Define the edges (transitions) between nodes
    workflow.add_edge(START, PLANNER_NODE)
    # Add conditional transitions based on decisions from the router
    workflow.add_conditional_edges(
        PLANNER_NODE,
        router_planner,  # Router determines the next action based on the current state
        {
            "continue": PLANNER_NODE,
            "task runner": HELPER_TOOLS_NODE,
            "__end__": END
        }
    )


    workflow.add_edge(HELPER_TOOLS_NODE, TOOL_NODE_NAME)
    workflow.add_edge(TOOL_NODE_NAME, PLANNER_NODE)
    # workflow.add_edge(QUASI_HUMAN_NODE, PLANNING_NODE_NAME)

    # Return the configured workflow graph
    return workflow


def router_planner(state: TeamState) -> Literal["task runner", "__end__", "continue"]:

    last_message = state.messages[-1]
    plan = state.plan

    if re.search(pattern_final_answer, f"{last_message.content} {plan}"):
        return "__end__"

    if re.search(pattern_helper, last_message.content):
        return "task runner"

    return "continue"
