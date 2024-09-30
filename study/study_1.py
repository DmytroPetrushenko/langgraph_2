from typing import Optional

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_anthropic import ChatAnthropic


# Pydantic
class Joke(BaseModel):
    """Joke to tell user."""

    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline to the joke")
    rating: Optional[int] = Field(
        default=None, description="How funny the joke is, from 1 to 10"
    )


def start_study():
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

    structured_llm = llm.with_structured_output(Joke)

    invoke = structured_llm.invoke("Tell me a joke about cats")

    print(invoke)

