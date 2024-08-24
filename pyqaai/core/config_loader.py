import os
import json
current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_file_path = os.path.join(current_directory, 'config.json')

from pyqaai.core.llm import LLM

def load_config():
    # Check if config file exists
    if not os.path.exists(config_file_path):
        # Create a default config file
        with open(config_file_path, 'w') as config_file:
            json.dump({"OPENAI_API_KEY": "", "OPENAI_ORGANIZATION": ""}, config_file)

    # Load existing config
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    
    return config

def save_config(config):
    with open(config_file_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def check_and_set_openai_credentials():
    config = load_config()

    # Check if OPENAI_API_KEY exists
    openai_api_key = config.get('OPENAI_API_KEY')
    openai_organization = config.get('OPENAI_ORGANIZATION')

    def validate_openai_credentials(api_key, organization=None):
        try:
            # Use the existing LLM object to generate a test response to validate credentials
            llm = LLM(api_key=api_key, organisation=organization)
            response = llm.generate_response(
                system_prompt="test",
                custom_override="test hello world. Please return JSON object as follows {'hello': 'world'}",
            )
            if (response.get('hello') == 'world'):
                return True
            else:
                print(f"Error: {str(response)}")
                return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    if not openai_api_key or not validate_openai_credentials(openai_api_key, openai_organization):
        print("The provided OPENAI_API_KEY is not valid or not found.")
        
        reenter_choice = input("Would you like to re-enter your API key and organization ID? (yes/no): ").strip().lower()
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

