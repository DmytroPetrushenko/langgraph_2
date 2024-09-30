from typing import List, Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from constants import PLANNING_EX_TEAM
from workflows.team_experimental.graph_planning_e1 import create_graph_planning_team_e1
from workflows.team_pentest.graph_handlers.graph_executor import launch_as_standalone_agent



def start_workflow_team_standalone_e1(
        input_message: Optional[str],
        model_llm: Optional[ChatOpenAI | ChatAnthropic] = None
):
    if input_message is None or model_llm is None:
        raise ValueError(
            "Something's missing! Either the input message or the model didn't show up. Time to investigate!"
        )

    graph = create_graph_planning_team_e1(
        model_llm=model_llm,
    )

    launch_as_standalone_agent(
        graph=graph,
        input_message=input_message,
        team_name=PLANNING_EX_TEAM
    )
