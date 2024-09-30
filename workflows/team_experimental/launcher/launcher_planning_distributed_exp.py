import forge
from workflows.team_experimental.executor_exp.stand_alone_exp import stand_alone_executor_experimental
from workflows.team_experimental.graph_planning_distributed import initialize_distributed_planning_graph


def launch_workflow_planning_distributed(input_msg: str):

    gpt_4o_mini = forge.create_llm('gpt-4o-mini')

    graph = initialize_distributed_planning_graph(model_llm=gpt_4o_mini)

    stand_alone_executor_experimental(
        graph=graph,
        input_message=input_msg,
        team_name='planning_distributed_experimental'
    )
