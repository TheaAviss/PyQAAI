import sys
import logging
import warnings
from dotenv import load_dotenv, set_key, dotenv_values
import os
import json
from core.code_analyser import CodeAnalyser
from core.user_interface import UserInterface
from static.constants import TASK_CHOICES
from core.llm import LLM
from static.prompts import SYSTEM_PROMPT, QA_PROMPTS, SYSTEM_PROMPT_IMPROVEMENT
from tqdm import tqdm
from termcolor import colored
from core.report_generator import HTMLReportGenerator

warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.CRITICAL + 1)

for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.CRITICAL + 1)

openai_api_key = None
openai_organization = None

def check_and_set_openai_credentials():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if OPENAI_API_KEY exists
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("OPENAI_API_KEY not found in .env file.")
        
        # Prompt user to input their API key
        openai_api_key = input("Please enter your OPENAI_API_KEY: ")
        
        # Save the API key to the .env file
        dotenv_file = ".env"
        set_key(dotenv_file, "OPENAI_API_KEY", openai_api_key)
        print("OPENAI_API_KEY has been saved to .env file.")
    
    # Check if OPENAI_ORGANIZATION exists
    openai_organization = os.getenv('OPENAI_ORGANIZATION')
    
    if not openai_organization:
        print("OPENAI_ORGANIZATION not found in .env file.")
        
        # Prompt user to input their organization ID
        openai_organization = input("Please enter your OPENAI_ORGANIZATION (if applicable): ")
        
        # Save the organization ID to the .env file
        if openai_organization:
            set_key(dotenv_file, "OPENAI_ORGANIZATION", openai_organization)
            print("OPENAI_ORGANIZATION has been saved to .env file.")
    
    return openai_api_key, openai_organization

def main():
    check_and_set_openai_credentials()

    code_analyser = CodeAnalyser()
    user_interface = UserInterface()
    llm = LLM(api_key=openai_api_key, organisation=openai_organization)
    

    file_path = user_interface.select_python_file()
    functions_classes = code_analyser.extract_functions_and_classes_from_module(file_path)
    
    if not functions_classes:
        print(f"No functions or classes found in {file_path}.")
        sys.exit(1)
    
    selected_function_class = user_interface.select_function_or_class(functions_classes)

    selected_task = user_interface.select_task(TASK_CHOICES)

    print(f"You selected: {selected_task}")
    print("---")
    report_generator = HTMLReportGenerator(report_file=f"qa_report_{selected_task}.html")
    report_generator.add_header(f"QA Report for {selected_task}", level=1)

    print("Extracting invoked functions...")
    invoked_functions = code_analyser.extract_callee_functions(file_path, selected_function_class)
    print(f"{len(invoked_functions)} invoked functions found in {selected_function_class}.\n\n")

    print("Extracting imported modules...")
    imported_modules, import_statements = code_analyser.get_imported_modules(file_path)
    local_imported_functions_classes = code_analyser.extract_local_imported_functions(imported_modules)
    print(f"{len(imported_modules)} imported modules found.\n\n")

    print("Extracting caller methods...")
    caller_methods = code_analyser.find_callers_of_function(selected_function_class)
    print(f"{len(caller_methods)} caller functions found.\n\n")
    
    qa_code = functions_classes[selected_function_class].code

    report_generator.add_summary(invoked_functions, imported_modules, caller_methods)

    report_generator.add_header("Selected Code Block", level=2)
    report_generator.add_code_block(qa_code)

    task_key = selected_task.split(":")[0].strip()
    
    if task_key in QA_PROMPTS:
        checks = QA_PROMPTS[task_key]
    else:
        print("Selected task does not match any known QA checks.")
        sys.exit(1)
    
    total_questions = sum(len(questions) for questions in checks.values())

    with tqdm(total=total_questions, desc="QA Check", unit="check", dynamic_ncols=True, leave=True) as pbar:
        filled_structure = []

        # Iterate over each category and its checks
        for category, questions in checks.items():
            report_generator.add_header(category, level=2)

            for question in questions:
                # Prepare the initial return structure
                return_structure = {
                    "qa_check_prompt": f"{category}: {question}",
                    "pass": "True or False",  # Placeholder for LLM to decide
                    "justification": "Detailed technical prose explanation in markdown for 'pass' verdict."  # Placeholder for LLM to provide reasoning
                }

                # Prepare the system prompt with the current question and return structure
                system_prompt = "\n".join(SYSTEM_PROMPT).format(filled_structure=return_structure)

                # Get the LLM response
                response = llm.generate_response(
                    system_prompt=system_prompt,
                    import_statements=import_statements,
                    local_imported_functions_classes=local_imported_functions_classes,
                    caller_methods=caller_methods,
                    qa_code=qa_code,
                    invoked_functions=invoked_functions
                )

                if response:
                    # Process the response and update the return structure accordingly
                    filled_structure.append(response)

                    # Check if the response passes
                    passed = response.get("pass") == "True"
                    justification = response.get("justification", "No justification provided.")
                    report_generator.add_result(question, passed, justification)

                    if passed:
                        # Update progress bar color and print question with a green checkmark
                        pbar.colour = "green"
                        tqdm.write(f"{category}: {question} {colored('✓', 'green')}")
                    else:
                        # Update progress bar color and print question with a red checkmark
                        pbar.colour = "red"
                        tqdm.write(f"{category}: {question} {colored('✗', 'red')}")
                else:
                    tqdm.write("Failed to generate a response.")
                
                # Update the progress bar
                pbar.update(1)

    print("------\n\n")
    print("Generating Suggested Code Improvements...")
    # CODE IMPROVEMENT SUGGESTIONS
    system_prompt = "\n".join(SYSTEM_PROMPT_IMPROVEMENT).format(qa_results="\n".join(report_generator.get_report_content()))

    response = llm.generate_response(
        system_prompt=system_prompt,
        import_statements=import_statements,
        local_imported_functions_classes=local_imported_functions_classes,
        caller_methods=caller_methods,
        qa_code=qa_code,
        invoked_functions=invoked_functions
    )

    if response:
        report_generator.add_header("Suggested Code Improvement:", level=2, index=4)
        report_generator.add_paragraph(response["changelog"], index=5)
        report_generator.add_code_block(response["suggested_code"], index=6)
        
    report_generator.save_report()
    report_generator.open_report()
    print("Completed all checks and generated report.")

if __name__ == "__main__":
    main()
