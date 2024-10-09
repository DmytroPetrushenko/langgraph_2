from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph, StateGraph

from utils.common_utils import save_and_open_graph
from utils.langraph.mapper import load_snapshot_from_json
from utils.langraph.mapper import save_snapshot_in_json

from constants import *


def stand_alone_executor_experimental(
        graph: StateGraph,
        input_message: str,
        team_name: str,
        live_mode: bool
):
    memory = MemorySaver()
    if live_mode:
        # Compile the graph with a memory-based checkpoint
        compiled_graph: CompiledStateGraph = graph.compile(checkpointer=memory)

        # Save and optionally open the compiled graph for further inspection
        save_and_open_graph(compiled_graph)

        # Execution configuration for the graph
        config = {"configurable": {"thread_id": 666}}

        # Initial input containing a human message (task description)
        inputs = {
            MESSAGES_FIELD: [
                HumanMessage(
                    content=input_message
                )
            ],
            SENDER_FIELD: ['human']
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

    elif not live_mode:
        # Compile the graph with a memory-based checkpoint
        graph.set_entry_point(PLAN_VALIDATOR_NODE)
        # Compile the graph with a memory-based checkpoint
        compiled_graph: CompiledStateGraph = graph.compile(checkpointer=memory)
        # Load a previously saved state snapshot from the provided file path
        state_snapshot = load_snapshot_from_json(
            file_path='resources/states/planning_distributed_experimental_snapshots_07_10_2024_13_21'
        )

        # Update the graph's state with the loaded snapshot
        updating_config = compiled_graph.update_state(state_snapshot.config, state_snapshot.values)

        # Stream the graph's execution from the specified node and print messages
        for event in compiled_graph.stream(None, updating_config, stream_mode='values'):
            message: AIMessage | HumanMessage = event['messages'][-1]
            message.pretty_print()
