from langchain_core.messages import HumanMessage, AIMessage
from langgraph.pregel import StateSnapshot

state = StateSnapshot(
    values={
        'messages': [
            HumanMessage(content='Investigate this host: 63.251.228.70.'),
            AIMessage(
                content="Certainly! I'll initiate an investigation of the host 63.251.228.70 and create a safety "
                        "report based on OWASP recommendations. To do this effectively, we'll need to gather more "
                        "information about the host. Let's start by involving the planning team to outline our "
                        "approach.\n\nPlanning team: Please help us create a structured plan to investigate the "
                        "host 63.251.228.70. We need to gather information about its potential vulnerabilities and "
                        "security posture. Include steps for reconnaissance, port scanning, and service "
                        "identification.",
                response_metadata={
                    'id': 'msg_019G79xEpiKsWRXASGJJxjz1',
                    'model': 'claude-3-5-sonnet-20240620',
                    'stop_reason': 'end_turn',
                    'stop_sequence': None,
                    'usage': {
                        'input_tokens': 162,
                        'output_tokens': 115
                    }
                },
                id='run-68156fb9-4f52-44a8-891a-3aa6e41eabce-0',
                usage_metadata={
                    'input_tokens': 162,
                    'output_tokens': 115,
                    'total_tokens': 277
                }
            )
        ],
        'sender': 'team_lead_node'
    },
    next=('planning_node',),
    config={
        'configurable': {
            'thread_id': 1,
            'checkpoint_ns': '',
            'checkpoint_id': '1ef6c349-aedf-6e14-8001-dc21e22a7942'
        }
    },
    metadata={
        'source': 'loop',
        'writes': {
            'team_lead_node': {
                'messages': [
                    AIMessage(
                        content="Certainly! I'll initiate an investigation of the host 63.251.228.70 and create "
                                "a safety report based on OWASP recommendations. To do this effectively, we'll "
                                "need to gather more information about the host. Let's start by involving the "
                                "planning team to outline our approach.\n\nPlanning team: Please help us create "
                                "a structured plan to investigate the host 63.251.228.70. We need to gather "
                                "information about its potential vulnerabilities and security posture. Include "
                                "steps for reconnaissance, port scanning, and service identification.",
                        response_metadata={
                            'id': 'msg_019G79xEpiKsWRXASGJJxjz1',
                            'model': 'claude-3-5-sonnet-20240620',
                            'stop_reason': 'end_turn',
                            'stop_sequence': None,
                            'usage': {
                                'input_tokens': 162,
                                'output_tokens': 115
                            }
                        },
                        id='run-68156fb9-4f52-44a8-891a-3aa6e41eabce-0',
                        usage_metadata={
                            'input_tokens': 162,
                            'output_tokens': 115,
                            'total_tokens': 277
                        }
                    )
                ],
                'sender': 'team_lead_node'
            }
        },
        'step': 1
    },
    created_at='2024-09-06T09:44:26.516133+00:00',
    parent_config={
        'configurable': {
            'thread_id': 1,
            'checkpoint_ns': '',
            'checkpoint_id': '1ef6c349-1042-6afe-8000-4920a8fe65ff'
        }
    }
)
