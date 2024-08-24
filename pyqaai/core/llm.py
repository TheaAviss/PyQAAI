from openai import OpenAI
import json
import os

class LLM:
    def __init__(self, api_key:str, organisation:str, model: str = "gpt-4o-2024-05-13", temperature: float = 0.0, stream: bool = False):
        # Get the API key from the environment variable
        self.client = OpenAI(organization=organisation, api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.stream = stream

    def _prepare_messages(self, system_prompt: str, import_statements: str, local_imported_functions_classes: str, caller_methods: str, qa_code: str, invoked_functions: str) -> list[dict[str, str]]:
        """
        Prepares the list of messages to send to the model, including system and user prompts.
        """

        user_message = (
            "--CODE STARTING--\n\n"
            f"Import Statements:\n{import_statements}\n\n"
            f"Locally Imported Functions/Classes:\n{local_imported_functions_classes}\n\n"
            f"Caller Methods:\n{caller_methods}\n\n"
            f"Invoked Functions:\n{invoked_functions}\n"
            "------\n"
            f"Code to perform QA Checks on:\n{qa_code}"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return messages


    def generate_response(self, system_prompt: str, import_statements: str, local_imported_functions_classes: str, caller_methods: str, qa_code: str, invoked_functions: str) -> dict | None:
        """
        Generates a response using the GPT model with the given inputs.
        """
        try:
            prepared_messages = self._prepare_messages(system_prompt, import_statements, local_imported_functions_classes, caller_methods, qa_code, invoked_functions)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=prepared_messages,
                temperature=self.temperature,
                stream=self.stream,
                response_format={ "type": "json_object" },
            )

            message = response.choices[0].message.content

            # print(f"Message: {message}")

            if response.choices[0]:
                content = json.loads(message)
                return content
            
            else:
                print("No content found in the response.")
                return None
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
