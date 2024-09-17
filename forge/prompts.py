from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_prompts(agent_anme: str, agent_description: str) -> ChatPromptTemplate:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                agent_description,
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name=agent_anme),
        ]
    )

    return prompt
