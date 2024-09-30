from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from utils.common_utils import save_and_open_graph
from utils.langraph.mapper import save_snapshot_in_json

from constants import *


def stand_alone_executor_experimental(
        graph,
        input_message,
        team_name
):
    memory = MemorySaver()

    # Compile the graph with a memory-based checkpoint
    compiled_graph: CompiledStateGraph = graph.compile(checkpointer=memory)

    # Save and optionally open the compiled graph for further inspection
    save_and_open_graph(compiled_graph)

    # Execution configuration for the graph
    config = {"configurable": {"thread_id": 666}}

    # Initial input containing a human message (task description)
    inputs = {
        "messages": [
            HumanMessage(
                content=input_message
            )
        ],
        'sender': 'human'
    }

    # Stream results from the graph execution and print the output
    for event in compiled_graph.stream(inputs, config, stream_mode='values'):
        message: AIMessage | HumanMessage = event['messages'][-1]

        # sender = event['sender']
        # name = names_mutation_dict.get(sender)
        # message.name = name if name else sender

        # Print the message
        message.pretty_print()


    # Save the states in a file
    states_list = list(compiled_graph.get_state_history(config=config))
    save_snapshot_in_json(
        states_list,
        team_name=team_name
    )
