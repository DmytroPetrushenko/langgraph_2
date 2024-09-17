from typing import Dict, Any

input_dict = {'args':{'module_category': 'auxiliary', 'module_name': 'scanner/http/http_version', 'options': {'RHOSTS': '63'
                                                                                                                '.251.228.70', 'RPORT': '80'}}}


def _process_input_args(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the input arguments and return a standardized dictionary.

    This function ensures that 'module_category' and 'module_name' are always present
    and that any 'options' field is flattened into the main dictionary.

    Args:
        kwargs: The input keyword arguments.

    Returns:
        A dictionary with a standardized structure, where 'options' are moved
        into the top-level dictionary if present.
    """
    match kwargs:
        case {'args': {'module_category': module_category, 'module_name': module_name, 'options': dict() as options}}:
            # Flatten 'options' into the main dictionary
            return {'module_category': module_category, 'module_name': module_name, **options}
        case {'args': {'module_category': module_category, 'module_name': module_name, **rest}}:
            # If there is no 'options', just return the remaining dictionary
            return {'module_category': module_category, 'module_name': module_name, **rest}
        case {'module_category': module_category, 'module_name': module_name, 'options': dict() as options}:
            # Flatten 'options' if it's directly in kwargs
            return {'module_category': module_category, 'module_name': module_name, **options}
        case {'module_category': module_category, 'module_name': module_name, **rest}:
            # Handle the case when there is no 'options' key
            return {'module_category': module_category, 'module_name': module_name, **rest}
        case _:
            raise ValueError("Invalid input structure")


result = _process_input_args(input_dict)
print(list(result.items()))
