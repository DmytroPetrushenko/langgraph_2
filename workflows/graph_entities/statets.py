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
    # List of messages exchanged within the team, dynamically combined via operator.add
    messages: Annotated[List[BaseMessage], operator.add] = Field(
        description="Messages exchanged within the team during the planning process."
    )

    # List of senders participating in the communication, dynamically combined via operator.add
    sender: Annotated[Optional[List[str]], operator.add] = Field(
        description="List of senders participating in the communication."
    )

    # The final security testing plan, optional field
    plan: Optional[str] = Field(
        default=None,
        description="A comprehensive security testing plan."
    )

    # List of subgroups relevant to the security testing process, dynamically combined via operator.add
    sub_groups: Annotated[Optional[List[str]], operator.add] = Field(
        default=None,
        description="List of subgroups used in the security testing process."
    )

    # List of modules chosen for security testing, dynamically combined via operator.add
    modules: Annotated[Optional[List[str]], operator.add] = Field(
        default=None,
        description="List of modules selected for the security testing process."
    )

    # Validator feedback field
    validator_feedback: Optional[str] = Field(
        default=None,
        description="Feedback from the plan validator regarding gaps or improvements."
    )
