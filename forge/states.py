from typing import TypedDict, Sequence, List, Dict, Optional

from langchain_core.messages import BaseMessage
from typing_extensions import Annotated
import operator
from pydantic import BaseModel, Field


class AgentStateComplicated(BaseModel):
    messages: Annotated[Sequence[BaseMessage], operator.add] = Field(
        default_factory=list,
        description="Sequence of messages exchanged during the penetration testing process"
    )
    sender: str = Field(
        default="",
        description="Identifier of the last entity that modified the state"
    )
    current_plan: Optional[List[str]] = Field(
        default=None,
        description="List of steps in the current penetration testing plan"
    )
    available_modules: List[str] = Field(
        default_factory=list,
        description="List of available Metasploit modules"
    )
    iteration_count: int = Field(
        default=0,
        description="Number of iterations the workflow has gone through"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "human", "content": "Create the penetration plan for IP 192.168.1.100"},
                    {"role": "ai", "content": "Understood. I'll start from getting sub port list."}
                ],
                "sender": "Strategy agent",
                "current_plan": ["Perform port scan on 192.168.1.100", "Analyze open ports",
                                 "Identify potential vulnerabilities"],
                "available_modules": ["auxiliary/scanner/portscan/tcp", "auxiliary/scanner/http/http_version"],
                "iteration_count": 1
            }
        }


class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], operator.add] = Field(
        default_factory=list,
        description="Sequence of messages exchanged during the penetration testing process"
    )
    sender: str = Field(
        default="",
        description="Identifier of the last entity that modified the state"
    )