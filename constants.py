# agents names
INITIALIZER = 'initializer'
EXECUTOR = 'executor'
PENTEST = 'pentest'
TEAM_LEAD = 'team_lead'
TASK_SUPERVISOR = 'task_supervisor'
HELPER = 'helper'
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
    '[*] Using code \'400\' as not found for'
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