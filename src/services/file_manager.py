import json
import os
from typing import Any

def save_data(data: Any, filename: str, append: bool = False):
    """
    Saves data to a JSON file. Supports appending to an existing file.
    """
    if append and os.path.exists(filename):
        existing_data = load_data(filename)
        if isinstance(existing_data, list) and isinstance(data, list):
            data = existing_data + data
        elif isinstance(existing_data, dict) and isinstance(data, dict):
            existing_data.update(data)
            data = existing_data
    
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_data(filename: str) -> Any:
    """
    Loads data from a JSON file. Returns an empty dictionary if file is missing.
    """
    if not os.path.exists(filename):
        return {}
    
   
def delete_data(filename: str):
    """
    Deletes a JSON file if it exists.
    """
    if os.path.exists(filename):
        os.remove(filename)

def update_data(filename: str, key: str, value: Any):
    """
    Updates a specific key in a JSON file if it exists.
    """
    data = load_data(filename)
    if isinstance(data, dict):
        data[key] = value
        save_data(data, filename)

def remove_key(filename: str, key: str):
    """
    Removes a specific key from a JSON file if it exists.
    """
    data = load_data(filename)
    if isinstance(data, dict) and key in data:
        del data[key]
        save_data(data, filename)