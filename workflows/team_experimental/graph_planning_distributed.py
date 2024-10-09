import functools
import re

from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from tools.msf_tools import get_msf_sub_groups_list, get_msf_exact_sub_group_modules_list
from utils import create_message_from_file
from workflows.graph_entities.agents import assistant_agent_with_tools, assistant_agent_without_tools, \
    assistant_agent_with_constructed_output
from workflows.graph_entities.nodes import *
from workflows.graph_entities.schemes import module_extraction_scheme, \
    plan_extraction_scheme, validator_feedback_scheme
from workflows.graph_entities.statets import PlanningTeamState

MODULE_GROUP_SELECTION_TOOLS = [get_msf_sub_groups_list]
MODULE_SELECTION_TOOLS = [get_msf_exact_sub_group_modules_list]
pattern_final_answer = re.compile(f"FINAL ANSWER")
counter_plan_node: int = 0


def initialize_distributed_planning_graph(
        model_llm: ChatOpenAI
):
    # get system message for the agents
    module_group_selection_sys_msg = create_message_from_file(MODULE_GROUP_SELECTION_MSG_PATH)
    module_selection_sys_msg = create_message_from_file(MODULE_SELECTION_MSG_PATH)
    extraction_sys_msg = create_message_from_file(EXTRACTION_MSG_PATH)
    plan_composition_sys_msg = create_message_from_file(PLAN_COMPOSITION_MSG_PATH)
    plan_validator_sys_msg = create_message_from_file(PLAN_VALIDATOR_MSG_PATH)

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

    module_extraction_agent = assistant_agent_with_constructed_output(
        system_message=extraction_sys_msg,
        model_llm=model_llm,
        oai_schema=module_extraction_scheme
    )

    plan_validator_agent = assistant_agent_without_tools(
        system_message=plan_validator_sys_msg,
        model_llm=model_llm
    )

    plan_composition_agent = assistant_agent_without_tools(
        system_message=plan_composition_sys_msg,
        model_llm=model_llm
    )

    plan_extraction_agent = assistant_agent_with_constructed_output(
        system_message=extraction_sys_msg,
        model_llm=model_llm,
        oai_schema=plan_extraction_scheme
    )

    validator_extraction_agent = assistant_agent_with_constructed_output(
        system_message=extraction_sys_msg,
        model_llm=model_llm,
        oai_schema=validator_feedback_scheme
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
        name=MODULE_SELECTION_NODE
    )

    module_extraction_node = functools.partial(
        create_module_extraction_node,
        agent=module_extraction_agent,
        name=MODULE_EXTRACTION_NODE
    )

    plan_validator_node = functools.partial(
        create_ordinary_node,
        agent=plan_validator_agent,
        name=PLAN_VALIDATOR_NODE
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
        create_module_extraction_node,
        agent=plan_extraction_agent,
        name=PLAN_EXTRACTION_NODE
    )

    validator_extraction_node = functools.partial(
        create_module_extraction_node,
        agent=validator_extraction_agent,
        name=VALIDATOR_EXTRACTION_NODE
    )

    # CREATE A GRAPH

    # Initialize the state graph with PlanningTeamState
    graph = StateGraph(PlanningTeamState)

    graph.add_node(MODULE_GROUP_SELECTION_NODE, module_group_selection_node)
    graph.add_node(MODULE_SELECTION_NODE, module_selection_node)
    graph.add_node(MODULE_EXTRACTION_NODE, module_extraction_node)
    graph.add_node(PLAN_VALIDATOR_NODE, plan_validator_node)
    graph.add_node(PLAN_COMPOSITION_NODE, plan_composition_node)
    graph.add_node(TASK_EXECUTION_NODE, task_execution_node)
    graph.add_node(PLAN_EXTRACTION_NODE, plan_extraction_node)
    graph.add_node(VALIDATOR_EXTRACTION_NODE, validator_extraction_node)

    graph.add_edge(START, MODULE_GROUP_SELECTION_NODE)

    graph.add_conditional_edges(
        MODULE_GROUP_SELECTION_NODE,
        router_module_group_section_node,
        {
            TASK_EXECUTION_NODE: TASK_EXECUTION_NODE,
            MODULE_EXTRACTION_NODE: MODULE_EXTRACTION_NODE
        }
    )

    graph.add_conditional_edges(
        MODULE_SELECTION_NODE,
        router_module_group_section_node,
        {
            TASK_EXECUTION_NODE: TASK_EXECUTION_NODE,
            MODULE_EXTRACTION_NODE: MODULE_EXTRACTION_NODE
        }
    )

    graph.add_conditional_edges(
        TASK_EXECUTION_NODE,
        router_task_execution_node,
        {
            MODULE_GROUP_SELECTION_NODE: MODULE_GROUP_SELECTION_NODE,
            MODULE_SELECTION_NODE: MODULE_SELECTION_NODE
        }
    )

    graph.add_conditional_edges(
        MODULE_EXTRACTION_NODE,
        router_module_extraction_node,
        {
            PLAN_COMPOSITION_NODE: PLAN_COMPOSITION_NODE,
            MODULE_SELECTION_NODE: MODULE_SELECTION_NODE
        }
    )

    graph.add_edge(PLAN_COMPOSITION_NODE, PLAN_EXTRACTION_NODE)
    graph.add_edge(PLAN_EXTRACTION_NODE, PLAN_VALIDATOR_NODE)
    graph.add_edge(PLAN_VALIDATOR_NODE, VALIDATOR_EXTRACTION_NODE)
    graph.add_edge(VALIDATOR_EXTRACTION_NODE, PLAN_COMPOSITION_NODE)

    graph.add_conditional_edges(
        PLAN_COMPOSITION_NODE,
        router_plan_composition_node,
        {
            PLAN_EXTRACTION_NODE: PLAN_EXTRACTION_NODE,
            "__end__": END
        }
    )

    return graph


def router_module_group_section_node(state: PlanningTeamState):
    last_message = state.messages[-1]

    if last_message.tool_calls:
        return TASK_EXECUTION_NODE

    return MODULE_EXTRACTION_NODE


def router_task_execution_node(state: PlanningTeamState):
    last_message = state.messages[-1]
    last_sender = state.sender[-1]

    if isinstance(last_message, ToolMessage):

        if last_sender in MODULE_GROUP_SELECTION_NODE:
            return MODULE_GROUP_SELECTION_NODE

        if last_sender in MODULE_SELECTION_NODE:
            return MODULE_SELECTION_NODE

    raise ValueError(f"Unexpected last_message class: '{last_message.__class__}' in task execution node. "
                     f"Expected -> ToolMessage class.")


def router_module_extraction_node(state: PlanningTeamState):
    pre_last_sender = state.sender[-2]

    if pre_last_sender is MODULE_GROUP_SELECTION_NODE:
        return MODULE_SELECTION_NODE

    if pre_last_sender is MODULE_SELECTION_NODE:
        return PLAN_COMPOSITION_NODE

    raise ValueError(f"Unexpected sender: '{pre_last_sender}' in {MODULE_EXTRACTION_NODE}. "
                     f"Expected -> {MODULE_GROUP_SELECTION_NODE} or {MODULE_SELECTION_NODE}.")



def router_plan_composition_node(state: PlanningTeamState):
    pre_last_sender = state.sender[-2]
    last_message = state.messages[-1]

    if (re.search(pattern_final_answer, f"{last_message.content}") or
            (pre_last_sender is VALIDATOR_EXTRACTION_NODE and counter_plan_node >= 3)):
        return "__end__"
    else:
        counter_plan_node += 1
        return PLAN_EXTRACTION_NODE
