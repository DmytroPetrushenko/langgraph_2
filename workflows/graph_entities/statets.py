import operator

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from pydantic import BaseModel, Field
from typing import Sequence, Annotated, Optional, List, Union


class TeamState(BaseModel):
    """
        Represents the state of a team within a graph.

        Attributes:
            messages (Sequence[BaseMessage]):
                A sequence of messages exchanged within the team. The messages are
                concatenated using `operator.add`, allowing for efficient message aggregation.

            sender (str):
                The identifier of the agent or entity that last sent a message.

            plan (str | None):
                The security testing plan created for the team. This field can be None
                if no plan has been assigned yet. It is primarily used to store structured
                information related to the team's operation strategy, which can be modified
                by the planner agent and executed by other team members.
    """

    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    plan: Optional[str] = Field(default=None, description="for a security testing plan")


class PlanningTeamState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    plan: Optional[str] = Field(
        default=None,
        description="A comprehensive security testing plan"
    )
    sub_groups: Annotated[Optional[List[str]], operator.add] = Field(
        default=None,
        description="List of subgroups used in the security testing process"
    )
    modules: Annotated[Optional[List[str]], operator.add] = Field(
        default=None,
        description="List of modules selected for the security testing process"
    )
