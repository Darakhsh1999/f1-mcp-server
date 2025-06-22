import json
from urllib.request import urlopen
from openf1_registry import f1_api, api_endpoints

### Essential tools ###

def get_api_endpoint(endpoint: str) -> dict:
    """
    Retrieve the API endpoint URL and filter metadata for a given OpenF1 endpoint.

    Args:
        endpoint (str): The name of the OpenF1 API endpoint (e.g., 'sessions', 'laps').

    Returns:
        dict: A dictionary containing:
            - status (str): 'success' if endpoint exists, 'error' otherwise
            - api_string (str): The full API URL for the endpoint
            - filter_metadata (dict): Available filters for the endpoint
    """
    try:
        url = f1_api.base_url + api_endpoints.get(endpoint, None)
        return {
            "status": "success",
            "api_string": url,
            "filter_metadata": f1_api.get_endpoint_filters(endpoint)
        }
    except:
        return {
            "status": "error",
            "api_string": f"Endpoint {endpoint} not found. Available endpoints: {f1_api.list_all_endpoints()}",
            "filter_metadata": dict()
        }


def get_filter_string(filter_name: str, filter_value: str, operator: str = "=") -> str:
    """
    Create a filter string for OpenF1 API requests.

    Args:
        filter_name (str): The name of the filter to apply.
        filter_value (str): The value to filter by.
        operator (str, optional): The comparison operator. Defaults to "=".

    Returns:
        str: Formatted filter string that can be appended to an API request.
    """
    return f"{filter_name}{operator}{filter_value}&"


def apply_filters(api_string: str, *filters: str) -> str:
    """
    Apply one or more filter strings to an API endpoint URL.

    Args:
        api_string (str): The base API endpoint URL.
        *filters (str): Variable number of filter strings to apply.

    Returns:
        str: The complete API URL with all filters applied.
    """
    if filters:
        for filter in filters:
            api_string += filter
    return api_string.rstrip("&") # Remove trailing & for last filter


def send_request(api_string: str) -> dict:
    """
    Send an HTTP GET request to the specified API endpoint and return the JSON response.

    Args:
        api_string (str): The complete API URL to send the request to.

    Returns:
        dict: The JSON response parsed as a Python dictionary.

    Raises:
        Exception: If there's an error during the HTTP request or JSON parsing.
    """
    try: 
        response = urlopen(api_string)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"Error: {e}")
        raise

### LLM helper functions ###

def get_api_endpoints() -> dict:
    """
    Retrieve a list of all available OpenF1 API endpoints.

    Returns:
        dict: A dictionary containing a single key 'endpoints' with a list of
              available endpoint names as strings.
    """
    return {
        "endpoints": f1_api.list_all_endpoints(),
    }


def get_endpoint_info(endpoint: str) -> dict:
    """
    Retrieve detailed information about a specific OpenF1 API endpoint.

    Args:
        endpoint (str): The name of the endpoint to get information about.

    Returns:
        dict: A dictionary containing:
            - endpoint (str): The name of the endpoint
            - endpoint_filters (list): Available filters for this endpoint
            - endpoint_help (str): Help text describing the endpoint's purpose and usage
    """
    return {
        "endpoint": endpoint,
        "endpoint_filters": f1_api.get_endpoint_filters(endpoint),
        "endpoint_help": f1_api.get_endpoint_help(endpoint)
    }


def get_filter_info(filter_name: str) -> dict:
    """
    Retrieve detailed information about a specific OpenF1 API filter.

    Args:
        filter_name (str): The name of the filter to get information about.

    Returns:
        dict: A dictionary containing:
            - filter_name (str): The name of the filter
            - filter_metadata (dict): Metadata about the filter, including
                                   description, valid values, and usage examples
    """
    return {
        "filter_name": filter_name,
        "filter_metadata": f1_api.get_filter_help(filter_name)
    }