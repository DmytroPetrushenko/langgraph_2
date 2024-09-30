from typing import Dict, Any


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


# Пример использования с вашим input_dict:
input_dict = {'module_category': 'auxiliary', 'module_name': 'scanner/http/atlassian_confluence_enum', 'args': {'RHOSTS': '34.241.130.103', 'RPORT': 8090}}

output = _extract_string_parameters(input_dict)
print(output)
