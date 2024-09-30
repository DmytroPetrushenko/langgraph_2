from langchain_core.messages import HumanMessage

import forge
import utils

from typing import Literal
import functools
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from tools.msf_tools import *


def create_graph(strategy_agent, checker_agent, tools):
    def router(state) -> Literal["call_tool", "check_plan", "__end__", "continue"]:
        messages = state["messages"]
        last_message = messages[-1]

        if last_message.tool_calls:
            return "call_tool"

        if "FINAL ANSWER" in last_message.content:
            if state["sender"] == "Strategy agent":
                return "check_plan"
            elif state["sender"] == "Checker agent":
                return "__end__"

        return "continue"

    workflow = StateGraph(forge.AgentState)

    # Create graph_entities
    strategy_node = functools.partial(strategy_agent, name="Strategy agent")
    checker_node = functools.partial(checker_agent, name="Checker agent")
    tool_node = ToolNode(tools)

    # Adding graph_entities to the graph
    workflow.add_node("Strategy agent", strategy_node)
    workflow.add_node("Checker agent", checker_node)
    workflow.add_node("call_tool", tool_node)

    # define paths in the graph
    workflow.set_entry_point("Strategy agent")

    workflow.add_edge("Strategy agent", "call_tool")
    workflow.add_edge("call_tool", "Strategy agent")
    workflow.add_edge("Strategy agent", "Checker agent")
    workflow.add_edge("Checker agent", "Strategy agent")

    # Adding conditional transitions
    workflow.add_conditional_edges(
        "Strategy agent",
        router,
        {
            "continue": "Strategy agent",
            "call_tool": "call_tool",
            "check_plan": "Checker agent",
            "__end__": END
        }
    )

    workflow.add_conditional_edges(
        "Checker agent",
        router,
        {
            "continue": "Strategy agent",
            "__end__": END
        }
    )

    return workflow.compile()


def start_workflow():
    llm_claude = forge.create_llm('Claude 3.5 Sonnet')

    tools = [get_msf_sub_groups_list, get_msf_exact_sub_group_modules_list, get_msf_module_options]

    strategy_agent = forge.create_agent_v2(llm=llm_claude, tools=tools, system_message='strategy#1.txt')
    checker_agent = forge.create_agent_v2(llm=llm_claude, system_message='checker#1.txt')

    graph = create_graph(strategy_agent, checker_agent, tools)


    for s in create_event(graph):
        utils.common_extract_content(s)
        print("\n<------------------------------------------>\n")


def create_event(graph):
    return graph.stream(
        {
            "messages": [
                HumanMessage(
                    content="please investigate 63.251.228.70"
                )
            ],
        },
        # Maximum number of steps to take in the graph
        {"recursion_limit": 30},
    )
