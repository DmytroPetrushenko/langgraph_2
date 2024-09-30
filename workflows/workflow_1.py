from typing import Literal

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

import constants
import forge
import utils
from tools.msf_tools import get_msf_sub_groups_list, get_msf_exact_sub_group_modules_list
from utils import create_message_from_file
from utils.common_utils import save_and_open_graph

STRATEGY_NODE = 'strategy node'
TOOL_NODE = 'tool node'
TOOLS = [get_msf_sub_groups_list, get_msf_exact_sub_group_modules_list]


def start_workflow():
    # Define a new graph
    workflow = StateGraph(forge.AgentState)

    # add graph_entities
    workflow.add_node(STRATEGY_NODE, strategy_node)
    workflow.add_node(TOOL_NODE, ToolNode(TOOLS))

    # add edges
    workflow.add_edge(START, STRATEGY_NODE)
    workflow.add_edge(TOOL_NODE, STRATEGY_NODE)

    # add custom edges
    workflow.add_conditional_edges(
        STRATEGY_NODE,
        route_strategy,
        {
            'continue': STRATEGY_NODE,
            'tools': TOOL_NODE,
            '__end__': END
        }
    )

    # compile
    graph = workflow.compile()

    # drawing the graph
    save_and_open_graph(graph)

    # initialization and startup of the graph
    event = create_event(graph)

    for s in event:
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


# Routes
def route_strategy(state: forge.AgentState) -> Literal["__end__", "tools", "continue"]:
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"

    if constants.FINAL_ANSWER in last_message.content:
        return "__end__"

    return "continue"


# creat strategy node
def strategy_node(state: forge.AgentState):
    messages = state.messages

    # Check that messages contains the expected data
    if not messages or not isinstance(messages, list):
        raise ValueError("State.messages must be a non-empty list.")

    # Create the prompt
    system_message = create_message_from_file('strategy#2.txt')
    if not system_message:
        raise ValueError("System message could not be created from file.")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("placeholder", "{msgs}")  # Check the correctness of the templating
    ])

    # Create the model and bind tools
    model = forge.create_llm('Claude 3.5 Sonnet')
    if not model:
        raise ValueError("Model could not be created.")

    model = model.bind_tools(TOOLS)
    if not model:
        raise ValueError("Model could not bind tools.")

    # Create the agent and get the response
    agent = prompt | model
    response = agent.invoke({'msgs': messages})

    if not response:
        raise ValueError("Agent did not return a valid response.")

    return {"messages": [response]}
