import os
import json
from typing import Optional, Tuple, Dict
current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_file_path = os.path.join(current_directory, 'config.json')

from pyqaai.core.llm import LLM

def load_config() -> Dict[str, str]:
    try:
        # Check if config file exists
        if not os.path.exists(config_file_path):
            # Create a default config file
            with open(config_file_path, 'w') as config_file:
                json.dump({"OPENAI_API_KEY": "", "OPENAI_ORGANIZATION": ""}, config_file)
                print(f"Created a new config file at {config_file_path}")

        # Load existing config
        with open(config_file_path, 'r') as config_file:
            config: Dict[str, str] = json.load(config_file)

        return config
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading config file: {e}")
        return {"OPENAI_API_KEY": "", "OPENAI_ORGANIZATION": ""}

def save_config(config: Dict[str, str], config_file_path: str) -> None:
    temp_file_path = config_file_path + '.tmp'

    try:
        with open(temp_file_path, 'w') as temp_file:
            json.dump(config, temp_file, indent=4)
        os.replace(temp_file_path, config_file_path)
    except (IOError, OSError) as e:
        print(f'Failed to save config: {e}')
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def validate_openai_credentials(api_key: str, organization: Optional[str] = None) -> bool:
    try:
        # Validate input parameters
        if not api_key:
            print("API key is required.")
            return False

        # Use the existing LLM object to generate a test response to validate credentials
        llm = LLM(api_key=api_key, organisation=organization)
        response: Dict[str, str] = llm.generate_response(
            system_prompt="test",
            custom_override="test hello world. Please return JSON object as follows {'hello': 'world'}",
        )

        if response.get('hello') == 'world':
            return True
        else:
            print(f"Unexpected response: {response}")
            return False
    except (ConnectionError, TimeoutError) as e:
        print(f"Network error: {str(e)}")
        return False
    except ValueError as e:
        print(f"Value error: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False


def check_and_set_openai_credentials() -> Tuple[str, Optional[str]]:
    config: Dict[str, str] = load_config()

    # Check if OPENAI_API_KEY exists
    openai_api_key: str = config.get('OPENAI_API_KEY')
    openai_organization: Optional[str] = config.get('OPENAI_ORGANIZATION')

    if not openai_api_key or not validate_openai_credentials(openai_api_key, openai_organization):
        print("The provided OPENAI_API_KEY is not valid or not found.")
        
        reenter_choice: str = input("Would you like to re-enter your API key and organization ID? (yes/no): ").strip().lower()
        if reenter_choice == 'yes':
            # Prompt user to input their API key
            openai_api_key = input("Please enter your OPENAI_API_KEY: ")

            # Optionally prompt for organization ID
            openai_organization = input("Please enter your OPENAI_ORGANIZATION (if applicable): ").strip() or None

            # Validate the new credentials
            if validate_openai_credentials(openai_api_key, openai_organization):
                config['OPENAI_API_KEY'] = openai_api_key
                config['OPENAI_ORGANIZATION'] = openai_organization
                save_config(config)
                print("The API key and organization ID have been saved to the config file.")
            else:
                print("Invalid credentials entered. Please check your API key and organization ID.")
        else:
            print("Continuing with existing configuration, but the credentials may not be valid.")

    return openai_api_key, openai_organization

