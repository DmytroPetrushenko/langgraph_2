import datetime
import logging
import re
import time
from typing import Optional, Tuple, List, Dict, Any

from pymetasploit3.msfrpc import MsfRpcClient
from langchain_core.tools import tool

from constants import *
from dao.sqlite.msf_sqlite import create_table, insert_data, create_connection, check_existing_record
from utils.dao.sqlalchemy.db_manager.alchemy_manager import ManagerAlchemyDB
from utils.msf.classes import CustomMsfRpcClient
from utils.msf.data_compressor import DataCompressor
from utils.task_time_logger import TaskTimeLogger

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

@tool
def msf_console_scan_tool(module_category: str, module_name: str, rhosts: str, rport: Optional[str] = None,
                          ports: Optional[str] = None, threads: int = 50, target: Optional[int] = None,
                          payload: Optional[str] = None, lhost: Optional[str] = None,
                          lport: Optional[str] = None) -> str:
    """
Execute a Metasploit module through the console interface and return the output.

Args:
    module_category: The category of the Metasploit module (e.g., 'auxiliary', 'exploit').
    module_name: The name of the Metasploit module (e.g., 'scanner/http/http_version').
    rhosts: The target hosts to scan.
    rport: The target port to scan. (Optional)
    ports: The target ports to scan. (Optional)
    threads: The number of threads to use for scanning. Default is 50.
    target: The specific target for the module. (Optional)
    payload: The payload to use with the module. (Optional)
    lhost: The local host for the payload. (Optional)
    lport: The local port for the payload. (Optional)

Returns:
    str: The output from the console after executing the module.

Example:
    output = msf_console_scan_tool('auxiliary', 'scanner/http/http_version', '3.255.212.92')
    print(output)
"""

    logger = TaskTimeLogger(f'{module_category}/{module_name}')
    logger.log_start()

    # Create database connection and create database
    db_connection = create_connection()
    logger.log_duration('Database connection created')

    table_name, table_fields = get_table_name_and_fields()

    if not create_table(db_connection, table_name, table_fields):
        logger.error('Table creation failed')
        raise Exception('Table creation failed')
    logger.log_duration('Table creation checked')

    if MOCK:
        record = check_existing_record(db_connection, f'{module_category}/{module_name}', rhosts)
        if record:
            # logger.info(
            #     f'The data was found in database for these parameters: {module_category}/{module_name}, {rhosts}')
            return record[0]

    # Create Metasploit RPC client
    logger.log_duration('RPC Client creation started')
    client: MsfRpcClient = CustomMsfRpcClient().get_client()
    logger.log_duration('RPC Client creation completed')

    # Create a new console
    current_console = client.consoles.console()

    try:
        commands = [
            f'use {module_category}/{module_name}',
            f'set RHOSTS {rhosts}',
            f'set THREADS {threads}'
        ]
        if 'scanner/portscan/tcp' in module_name:
            commands.append(f'set CONCURRENCY 100')
        if rport:
            commands.append(f'set RPORT {rport}')
        if ports:
            commands.append(f'set PORTS {ports}')
        if target:
            commands.append(f'set TARGET {target}')
        if payload:
            commands.append(f'set PAYLOAD {payload}')
        if lhost:
            commands.append(f'set LHOST {lhost}')
        if lport:
            commands.append(f'set LPORT {lport}')
        commands.append('run')

        command_str = '\n'.join(commands) + '\n'
        current_console.write(command_str)

        logger.log_duration('the command was created and sent to msfconsole.')

        # Record the start time
        start_time = time.time()

        output = ""
        while True:
            response = current_console.read()
            if response['data']:
                # print(response['data'])
                output += response['data']
                # print(response['data'])

            if any(keyword in output for keyword in EXECUTION_COMPLETION_PHRASES):
                break

            # Check for timeout
            if time.time() - start_time > TIMEOUT:
                timeout_message = '[TIMEOUT] "Time limit exceeded, exiting the loop."'
                output += timeout_message
                logger.warning(timeout_message)

                # Stop the task in Metasploit
                current_console.write('exit\n')
                break

            time.sleep(1)
    finally:
        # Destroy the console
        current_console.destroy()

    logger.log_duration(f'This task was executed! Next, data will be cleaned and written into the database!')

    # Split the output at the documentation line and take the part after it
    split_output = re.split(r'Metasploit Documentation: https://docs.metasploit.com/\n', output, maxsplit=1)
    filtered_output = split_output[1] if len(split_output) > 1 else ""
    compressed_output: str | None = None
    if should_use_compressor(filtered_output, min_lines=15, patterns=[r'\[\*\]']):
        compressor = DataCompressor()
        compressor.start_compressing(filtered_output)
        compressed_output = compressor.get_compressed_output()

    # Insert the result into the database
    table_values = {
        'module': f'{module_category}/{module_name}',
        'rhosts': rhosts,
        'rport': rport or '0',
        'ports': ports or '',
        'threads': threads,
        'duration': logger.get_duration(),
        'output': filtered_output,
        'compressed_output': str(compressed_output)
    }
    insert_data(db_connection, table_name, table_values, logger)

    return compressed_output if compressed_output else filtered_output


def get_table_name_and_fields() -> Tuple[str, dict]:
    """
    Generate the table name and define the table fields.

    Returns:
        tuple: A tuple containing the table name and a dictionary of table fields.
    """
    table_name = TABLE_NAME if TABLE_NAME else f'msf_console_{datetime.datetime.now().strftime("%Y_%m_%d")}'
    table_fields = {
        'id': ['INTEGER', 'PRIMARY KEY', 'AUTOINCREMENT'],
        'module': ['TEXT', 'NOT NULL'],
        'rhosts': ['TEXT', 'NOT NULL'],
        'rport': ['INTEGER'],
        'ports': ['TEXT'],
        'threads': ['INTEGER'],
        'output': ['TEXT'],
        'compressed_output': ['TEXT'],
        'duration': ['TEXT']
    }
    return table_name, table_fields


def should_use_compressor(text: str, min_lines: int = 10, patterns: List[str] = [r'\[\*\]']) -> bool:
    lines = text.splitlines()
    if len(lines) > min_lines:
        return True
    if patterns:
        for pattern in patterns:
            if any(re.search(pattern, line) for line in lines):
                return True
    return False


from typing import List, Tuple


@tool
def get_msf_sub_groups_list() -> List[str]:
    """
    Retrieves a list of unique 'sub_group' names from the 'module_auxiliary' table in the specified database.

    This function allows agents to obtain available subgroups for further processing or categorization.

    :param db_url: The database connection URL. Defaults to 'sqlite:///metasploit_data.db'.
    :type db_url: str
    :return: A list of unique sub_group names.
    :rtype: List[str]
    """
    db_url: str = 'sqlite:///metasploit_data.db'
    try:
        manager_db = ManagerAlchemyDB(db_url)
        sub_groups = manager_db.get_sub_group_from_modules()
        return sub_groups
    except Exception as e:
        print(f"Failed to retrieve sub_group list: {e}")
        return []


@tool
def get_msf_exact_sub_group_modules_list(sub_group_name: str, db_url: str = 'sqlite:///metasploit_data.db') -> List[Tuple[str, str]]:
    """
    Retrieves a list of modules by their 'sub_group' from the 'module_auxiliary' table.

    This function is useful for agents that need to filter modules by specific sub-groups.
    The sub_group_name should be formatted using slashes (e.g., 'auxiliary/admin').

    :param db_url: The database connection URL.
    :type db_url: str
    :param sub_group_name: The name of the sub_group to filter modules by, in the format 'category/name' (e.g., 'exploit/multi').
    :type sub_group_name: str
    :return: A list of tuples, where each tuple contains the name and description of a module.
    :rtype: List[Tuple[str, str]]
    """
    try:
        manager_db = ManagerAlchemyDB(db_url)
        modules = manager_db.get_modules_by_sub_group(sub_group_name)
        return modules
    except Exception as e:
        print(f"Failed to retrieve modules for sub_group '{sub_group_name}': {e}")
        return []



@tool
def get_msf_module_options(module_name: str, db_url: str = 'sqlite:///metasploit_data.db') -> str:
    """
    Retrieves all non-null options for a given Metasploit module from the 'module_options_auxiliary' table.

    This function is intended for agents that need to extract and work with specific configuration options of
    Metasploit modules.

    Args:
        module_name (str): The name of the Metasploit module to retrieve options for.
        db_url (str, optional): The database connection URL. Defaults to 'sqlite:///metasploit_data.db'.

    Returns:
        str: A formatted string with the non-null option values for the specified module, or an empty string if
        an error occurs.
    """
    try:
        manager_db = ManagerAlchemyDB(db_url)
        # Retrieve module options and filter out null values
        modules = [module for module in manager_db.get_module_options(module_name) if module]
        # Format and return the options as a string
        return f'Configuration options for this module -> {module_name}: {", ".join(modules)}'
    except Exception as e:
        # Handle exceptions and print an error message
        print(f"Failed to retrieve options for module '{module_name}': {e}")
        return ''


@tool
def msf_console_scan_tool_dynamic(input_dict: Any) -> str:
    """
    Execute a Metasploit module through the console interface and return the output.

    This function can handle various input structures, including nested dictionaries
    and flat structures for module category and name. It processes the input,
    executes the specified Metasploit module (or a mock version), and returns the output.

    Args:
        input_dict: Dictionary containing the module configuration and parameters.
                    Must include 'module_category' and 'module_name', either at the
                    top level or within a nested 'args' dictionary.

    Returns:
        str: The output from the console after executing the module, or an error message
             if execution fails.

    Raises:
        ValueError: If required arguments ('module_category' or 'module_name') are missing.
        Exception: For any other errors during execution. These are caught and returned
                   as error messages in the output string.
    """

    try:
        # Process and standardize the input arguments
        args = _extract_string_parameters(input_dict)

        # Check if required arguments are present
        if 'module_category' not in args or 'module_name' not in args:
            raise ValueError("Both 'module_category' and 'module_name' are required.")

        # Extract and remove module_category and module_name from args
        module_category = args.pop('module_category')
        module_name = args.pop('module_name')

        # Get a host for inserting in the DB
        host: Optional[str] = None
        for host_name in HOST_NAMES_LIST:
            if host_name in args.keys():
                host = args.get(host_name)
                break
        if not host:
            logger.warning("Host is absent; other args will be added to the DB instead of the host.")
            host = '; '.join([f'{key}: {value}' for key, value in args.items()])

        # If mock mode is enabled, return mock execution results
        if MOCK_MSF_TOOLS and host:
            result = _mock_execution(module_category, module_name, host)
            if result and isinstance(result, str):
                return result

        # Execute the actual Metasploit module
        output = _execute_metasploit_module(module_category, module_name, args)

        # Split the output at the documentation line and take the part after it
        split_output = re.split(r'Metasploit Documentation: https://docs.metasploit.com/\n', output, maxsplit=1)
        filtered_output = split_output[1] if len(split_output) > 1 else ""

        # Compressing output data
        compressor = DataCompressor()
        compressor.start_compressing(filtered_output)
        compressed_output = compressor.get_compressed_output()

        # Save the results in the SQLite DB
        _save_results_db(
            module=f'{module_category}/{module_name}',
            host=host,
            output=filtered_output,
            compressed_output=compressed_output
        )

        return compressed_output

    except ValueError as e:
        return f"ValueError: {str(e)}"
    except Exception as e:
        logger.error("An unexpected error occurred during Metasploit module execution.", exc_info=True)
        raise


def _extract_string_parameters(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Recursively extracts all key-value pairs from the input dictionary
    where the value is a string, ignoring the nesting structure of the dictionary.

    Args:
        data (dict): The input dictionary, which can contain nested dictionaries.

    Returns:
        dict: A dictionary containing only the key-value pairs where the value is a string.
    """
    params = {}

    # Iterate through each key-value pair in the dictionary
    for k, v in data.items():
        # If the value is a string, add it to the result
        if isinstance(v, (int, float, bool, str)):
            params[k] = v
        # If the value is another dictionary, recursively process it
        elif isinstance(v, dict):
            params.update(_extract_string_parameters(v))

    return params



def _save_results_db(host: str, module: str, output: str, compressed_output: str) -> None:
    manager_db = ManagerAlchemyDB(db_url='sqlite:///my_sqlite.db')
    manager_db.write_to_db(
        host=host,
        module=module,
        output=output,
        compressed_output=compressed_output
    )


def _mock_execution(module_category: str, module_name: str, host: str) -> str:
    db_connection = create_connection()
    record = check_existing_record(db_connection, f'{module_category}/{module_name}', host)
    if record:
        return record[0]
    else:
        print("Mock execution: No existing record found.")


def _execute_metasploit_module(module_category: str, module_name: str, args: Dict[str, Any]) -> str:
    client: MsfRpcClient = CustomMsfRpcClient().get_client()
    current_console = client.consoles.console()

    try:
        commands = [f'use {module_category}/{module_name}']
        commands.extend(_build_module_commands(args))

        if module_category is 'exploit':
            commands.append('exploit')
        else:
            commands.append('run')

        command_str = '\n'.join(commands) + '\n'
        current_console.write(command_str)

        return _read_console_output(current_console, TIMEOUT)

    finally:
        current_console.destroy()


def _build_module_commands(args: Dict[str, Any]) -> list:
    return [f"set {key} {value}" for key, value in args.items()]


def _read_console_output(console, timeout: int = 300) -> str:
    start_time = time.time()
    output = ""
    while True:
        response = console.read()
        output += response['data']

        if any(phrase in output for phrase in EXECUTION_COMPLETION_PHRASES):
            break

        if time.time() - start_time > timeout:
            output += '[TIMEOUT] "Time limit exceeded, exiting the loop."'
            console.write('exit\n')
            break

        time.sleep(1)
    return output
