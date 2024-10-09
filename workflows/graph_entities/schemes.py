from constants import *

planning_team_state_schema = {
    "title": "PlanningTeamState",
    "description": "A structured output representing the state of a planning team.",
    "type": "object",
    "properties": {
        MESSAGES_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Messages exchanged within the team during the planning process."
        },
        SENDER_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of senders participating in the communication."
        },
        PLAN_FIELD: {
            "type": "string",
            "description": "A comprehensive security testing plan."
        },
        SUB_GROUPS_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of subgroups used in the security testing process."
        },
        MODULES_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of modules selected for the security testing process."
        }
    },
    "required": [MESSAGES_FIELD, SENDER_FIELD, PLAN_FIELD, SUB_GROUPS_FIELD, MODULES_FIELD]
}


module_extraction_scheme = {
    "title": "module_extraction_scheme",
    "description": "A structured output representing selected Metasploit module groups and specific modules for the "
                   "state of a testing team.",
    "type": "object",
    "properties": {
        SUB_GROUPS_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "A list of selected Metasploit module groups that are relevant for the testing task."
        },
        MODULES_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "A list of specific Metasploit modules chosen from the provided module groups."
        }
    },
    "required": [SUB_GROUPS_FIELD, MODULES_FIELD]
}


plan_extraction_scheme = {
    "title": "plan_extraction_scheme",
    "description": "A field representing the final security testing plan.",
    "type": "object",
    "properties": {
        PLAN_FIELD: {
            "type": "string",
            "description": "The final security testing plan."
        }
    },
    "required": [PLAN_FIELD]
}

validator_feedback_scheme = {
    "title": "validator_feedback_scheme",
    "description": "A field representing the feedback provided by the validator on the security testing plan.",
    "type": "object",
    "properties": {
        VALIDATOR_FIELD: {
            "type": "string",
            "description": "Feedback from the validator about the plan."
        }
    },
    "required": [VALIDATOR_FIELD]
}
