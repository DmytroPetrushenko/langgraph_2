import functools
import re

from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from constants import *
from tools.msf_tools import get_msf_sub_groups_list, get_msf_exact_sub_group_modules_list
from utils import create_message_from_file
from workflows.graph_entities.agents import assistant_agent_with_tools, assistant_agent_without_tools, \
    assistant_agent_with_constructed_output
from workflows.graph_entities.nodes import create_ordinary_node, create_tool_node, create_node_with_construct_output, \
    create_extraction_node
from workflows.graph_entities.statets import PlanningTeamState


MODULE_GROUP_SELECTION_TOOLS = [get_msf_sub_groups_list]
MODULE_SELECTION_TOOLS = [get_msf_exact_sub_group_modules_list]


def initialize_distributed_planning_graph(
        model_llm: ChatOpenAI
):
    # get system message for the agents
    module_group_selection_sys_msg = create_message_from_file(MODULE_GROUP_SELECTION_MSG_PATH)
    module_selection_sys_msg = create_message_from_file(MODULE_SELECTION_MSG_PATH)
    plan_composition_sys_msg = create_message_from_file(PLAN_COMPOSITION_MSG_PATH)
    module_organizer_sys_msg = create_message_from_file(MODULE_ORGANIZER_MSG_PATH)

    # CREATE THE AGENTS
    module_group_selection_agent = assistant_agent_with_tools(
        system_message=module_group_selection_sys_msg,
        model_llm=model_llm,
        tools=MODULE_GROUP_SELECTION_TOOLS
    )

    module_selection_agent = assistant_agent_with_tools(
        system_message=module_selection_sys_msg,
        model_llm=model_llm,
        tools=MODULE_SELECTION_TOOLS
    )

    module_organizer_agent = assistant_agent_without_tools(
        system_message=module_organizer_sys_msg,
        model_llm=model_llm
    )

    plan_composition_agent = assistant_agent_without_tools(
        system_message=plan_composition_sys_msg,
        model_llm=model_llm
    )

    plan_extraction_agent = assistant_agent_with_constructed_output(
        system_message='planning_team/plan_extraction_agent#1.txt',
        model_llm=model_llm
    )

    # CREATE THE NODES AND EDGES
    module_group_selection_node = functools.partial(
        create_ordinary_node,
        agent=module_group_selection_agent,
        name=MODULE_GROUP_SELECTION_NODE
    )

    module_selection_node = functools.partial(
        create_ordinary_node,
        agent=module_selection_agent,
        name=MODULE_GROUP_SELECTION_NODE
    )

    module_extraction_node = functools.partial(
        create_extraction_node,
        name=MODULE_EXTRACTION_NODE
    )

    module_organizer_node = functools.partial(
        create_ordinary_node,
        agent=module_organizer_agent,
        name=MODULE_ORGANIZER_NODE
    )

    plan_composition_node = functools.partial(
        create_ordinary_node,
        agent=plan_composition_agent,
        name=PLAN_COMPOSITION_NODE
    )

    combined_tools = [*MODULE_GROUP_SELECTION_TOOLS, *MODULE_SELECTION_TOOLS]
    task_execution_node = functools.partial(
        create_tool_node,
        tools=combined_tools
    )

    plan_extraction_node = functools.partial(
        create_node_with_construct_output,
        agent=plan_extraction_agent,
        name=PLAN_EXTRACTION_NODE
    )

    # CREATE A GRAPH

    # Initialize the state graph with PlanningTeamState
    graph = StateGraph(PlanningTeamState)

    graph.add_node(MODULE_GROUP_SELECTION_NODE, module_group_selection_node)
    graph.add_node(MODULE_SELECTION_NODE, module_selection_node)
    graph.add_node(MODULE_EXTRACTION_NODE, module_extraction_node)
    graph.add_node(MODULE_ORGANIZER_NODE, module_organizer_node)
    graph.add_node(PLAN_COMPOSITION_NODE, plan_composition_node)
    graph.add_node(TASK_EXECUTION_NODE, task_execution_node)
    graph.add_node(PLAN_EXTRACTION_NODE, plan_extraction_node)

    graph.add_edge(START, MODULE_GROUP_SELECTION_NODE)
    graph.add_conditional_edges(
        MODULE_GROUP_SELECTION_NODE,
        router,
        {
            "continue": MODULE_GROUP_SELECTION_NODE,
            TASK_EXECUTION_NODE: TASK_EXECUTION_NODE
        }
    )
    graph.add_conditional_edges(
        MODULE_SELECTION_NODE,
        router,
        {
            "continue": MODULE_SELECTION_NODE,
            TASK_EXECUTION_NODE: TASK_EXECUTION_NODE
        }
    )

    graph.add_edge(TASK_EXECUTION_NODE, MODULE_EXTRACTION_NODE)

    graph.add_conditional_edges(
        MODULE_EXTRACTION_NODE,
        router_module_extraction_node,
        {
            MODULE_SELECTION_NODE: MODULE_SELECTION_NODE,
            MODULE_ORGANIZER_NODE: MODULE_ORGANIZER_NODE
        }
    )

    graph.add_conditional_edges(
        PLAN_COMPOSITION_NODE,
        router_plan_composition_node,
        {
            PLAN_EXTRACTION_NODE: PLAN_EXTRACTION_NODE,
            "continue": PLAN_COMPOSITION_NODE
        }
    )
    graph.add_edge(MODULE_ORGANIZER_NODE, PLAN_COMPOSITION_NODE)
    graph.add_edge(PLAN_EXTRACTION_NODE, END)

    return graph


def router(state: PlanningTeamState) -> str:
    last_message = state.messages[-1]

    if last_message.tool_calls:
        return TASK_EXECUTION_NODE

    return "continue"


def router_module_extraction_node(state: PlanningTeamState) -> str:
    if state.sender == MODULE_SELECTION_NODE:
        return MODULE_ORGANIZER_NODE

    if state.sender == MODULE_GROUP_SELECTION_NODE:
        return MODULE_SELECTION_NODE

    raise ValueError(f"Unexpected sender '{state.sender}' in task execution node. "
                     f"Expected one of: {MODULE_SELECTION_NODE}, {MODULE_GROUP_SELECTION_NODE}.")


def router_plan_composition_node(state: PlanningTeamState) -> str:
    last_message = state.messages[-1]
    plan = state.plan

    if re.search(r'FINAL_ANSWER', f"{last_message.content} {plan}"):
        return PLAN_EXTRACTION_NODE

    return "continue"
