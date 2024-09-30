# agents names
INITIALIZER = 'initializer'
EXECUTOR = 'executor_exp'
PENTEST = 'pentest'
TEAM_LEAD = 'team_lead'
TASK_SUPERVISOR = 'task_supervisor'
HELPER = 'helper_agent'
EXAMPLE = 'example'

# path to msf modules names
REPLACEMENT_PRELIMINARY_MODULES = 'msf_modules/preliminary_modules.txt'
REPLACEMENT_AUXILIARY_MODULES = 'msf_modules/auxiliary_modules.txt'

# placeholders
TEXT_INSIDE_BRACES_PATTERN = r'\{(.*?)\}'

# others
PREFIX_REPLACEMENT = 'REPLACEMENT_'
DEFAULT_MESSAGE = 'default_message.txt'

PASSWORD = 'PASSWORD'
HOST = 'HOST'
PORT = 'PORT'
SSL = 'SSL'
FALSE = 'false'

# msf_tools.py constant
EXECUTION_COMPLETION_PHRASES = [
    'execution completed',
    'OptionValidateError',
    '[-] Unknown command: run.',
    '[*] Exploit completed, but no session was created.',
    '[*] Using code \'400\' as not found for',
    '[-] Unknown command:'
]
TIMEOUT = 600  # 10 minutes

# importing_msfinfo_database.py
DELETE_UNTIL = '#     Name'

# some flag
MOCK: bool = False
MOCK_MSF_TOOLS: bool = False

# database
TABLE_NAME: str | None = None

# file path
MESSAGE_FOLDER = 'messages'

# end key
FINAL_ANSWER = "FINAL ANSWER"

# msf_tools.py
HOST_NAMES_LIST = ['RHOSTS', 'rhosts']

TESTING_NODE = "Attack Coordinator"
PLANNER_NODE = "Operation Planner"
QUASI_HUMAN_NODE = "Qausi Human"
HELPER_TOOLS_NODE = 'Task Runner'

PLANNING_TEAM = 'Planning Team'
TESTING_TEAM = 'Testing team'
PLANNING_EX_TEAM = 'Planning Experimental Team'

# planning distributed team
MODULE_GROUP_SELECTION_NODE = 'module_group_selection_node'
MODULE_SELECTION_NODE = 'module_selection_node'
MODULE_ORGANIZER_NODE = "module_organizer_node"
PLAN_COMPOSITION_NODE = 'plan_composition_node'
TASK_EXECUTION_NODE = 'task_execution_node'
PLAN_EXTRACTION_NODE = 'plan_extraction_node'
MODULE_EXTRACTION_NODE = 'module_extraction_node'

names_mutation_dict = {
    MODULE_GROUP_SELECTION_NODE: 'MODULE GROUP SELECTION AGENT',
    MODULE_SELECTION_NODE: 'MODULE SELECTION AGENT',
    MODULE_ORGANIZER_NODE: 'MODULE ORGANIZER AGENT',
    PLAN_COMPOSITION_NODE: 'PLAN COMPOSITION AGENT',
    TASK_EXECUTION_NODE: 'TASK EXECUTION AGENT',
    PLAN_EXTRACTION_NODE: 'PLAN EXTRACTION AGENT'
}

MODULE_GROUP_SELECTION_MSG_PATH = 'planning_team/module_group_selection_agent#1.txt'
MODULE_SELECTION_MSG_PATH = 'planning_team/module_selection_agent#1.txt'
PLAN_COMPOSITION_MSG_PATH = 'planning_team/plan_composition_agent#1.txt'
PLAN_EXTRACTION_MSG_PATH = 'planning_team/plan_extraction_agent#1.txt'
MODULE_ORGANIZER_MSG_PATH = 'planning_team/module_organizer_agent#1.txt'
