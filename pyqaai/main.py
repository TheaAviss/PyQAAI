import sys
import logging
import warnings
from dotenv import load_dotenv, set_key, dotenv_values
import os
import json
from tqdm import tqdm
from termcolor import colored

from pyqaai.core.code_analyser import CodeAnalyser
from pyqaai.core.user_interface import UserInterface
from pyqaai.static.constants import TASK_CHOICES, WELCOME_MESSAGE
from pyqaai.core.llm import LLM
from pyqaai.static.prompts import SYSTEM_PROMPT, QA_PROMPTS, SYSTEM_PROMPT_IMPROVEMENT
from pyqaai.core.report_generator import HTMLReportGenerator
from pyqaai.core.config_loader import check_and_set_openai_credentials

warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.CRITICAL + 1)

for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.CRITICAL + 1)

def main():
    print(WELCOME_MESSAGE)
    print(f"Current Working Directory: {os.getcwd()}\n")

    try:
        openai_api_key, openai_organization = check_and_set_openai_credentials()
    except Exception as e:
        print(f"Error retrieving OpenAI credentials: {e}")
        sys.exit(1)

    code_analyser = CodeAnalyser()
    user_interface = UserInterface()
    llm = LLM(api_key=openai_api_key, organisation=openai_organization)
    
    try:
        file_path = user_interface.select_python_file()
        if file_path is None:
            print("Exiting...")
            sys.exit(1)
        functions_classes = code_analyser.extract_functions_and_classes_from_module(file_path)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)
    
    if not functions_classes:
        print(f"No functions or classes found in {file_path}.")
        sys.exit(1)
    
    selected_function_class_full = user_interface.select_function_or_class(functions_classes)
    if selected_function_class_full is None:
        print("Exiting...")
        sys.exit(1)
    selected_function_class = selected_function_class_full.split(".")[-1]

    selected_task = user_interface.select_task(TASK_CHOICES)
    if selected_task is None:
        print("Exiting...")
        sys.exit(1)

    print(f"You selected: {selected_task}")
    print("---")
    report_generator = HTMLReportGenerator(report_file=f"qa_report_{selected_task.replace(' ', '_').replace(':', '_')}.html")
    report_generator.add_header(f"QA Report for {selected_task}", level=1)

    print("Extracting invoked functions...")
    invoked_functions = code_analyser.extract_callee_functions(file_path, selected_function_class)
    if len(invoked_functions) > 0:
        print(f"{colored('✓', 'green')} {len(invoked_functions)} invoked functions found in {selected_function_class}.\n\n")
    else:
        print(f"{len(invoked_functions)} invoked functions found in {selected_function_class}.\n\n")

    print("Extracting imported modules...")
    imported_modules, import_statements = code_analyser.get_imported_modules(file_path)
    local_imported_functions_classes = code_analyser.extract_local_imported_functions(imported_modules)
    if len(imported_modules) > 0:
        print(f"{colored('✓', 'green')} {len(imported_modules)} imported modules processed.\n\n")
    else:
        print(f"{len(imported_modules)} imported modules processed.\n\n")

    print("Extracting caller methods...")
    caller_methods = code_analyser.find_callers_of_function(selected_function_class)
    if len(caller_methods) > 0:
        print(f"{colored('✓', 'green')} {len(caller_methods)} caller functions found.\n\n")
    else:
        print(f"{len(caller_methods)} caller functions found.\n\n")
    
    qa_code = functions_classes[selected_function_class_full].code

    report_generator.add_summary(invoked_functions, imported_modules, caller_methods)

    report_generator.add_header("Selected Code Block", level=2)
    report_generator.add_code_block(qa_code)

    task_key = selected_task.split(":")[0].strip()

    if task_key == "Custom Task":
        print("Custom Task Selected. Code analysis has been performed to gather relevant code. The AI will now carry out your custom task with the relevant code.")
        custom_prompt = input("Please enter your custom prompt: ")

        # Prepare the initial return structure
        return_structure = {
            "custom_qa_check_prompt": custom_prompt,
            "answer": "Detailed technical prose explanation in markdown. No code at all. This section should be for planning in technical detail what should be done to fulfill the request or answering custom QA questions."  # Placeholder for LLM to provide reasoning
        }

        # Prepare the system prompt with the custom question and return structure
        system_prompt = "\n".join(SYSTEM_PROMPT).format(filled_structure=return_structure)

        response = llm.generate_response(
            system_prompt=system_prompt,
            import_statements=import_statements,
            local_imported_functions_classes=local_imported_functions_classes,
            caller_methods=caller_methods,
            qa_code=qa_code,
            invoked_functions=invoked_functions
        )

        if response:
            answer = response.get("answer", "No answer provided.")
            report_generator.add_result(custom_prompt, "True", answer)

            print(colored("Response Received ✓", "green"))

        else:
            print(colored("Failed to generate a response ✗", "red"))
            print("Failed to generate a response.")

    elif task_key in QA_PROMPTS:
        checks = QA_PROMPTS[task_key]
        total_questions = len(checks.items())

        with tqdm(total=total_questions, desc="QA Check", unit="check", dynamic_ncols=True, leave=True) as pbar:
            filled_structure = []

            # Iterate over each category and its checks
            for category, question in checks.items():
                report_generator.add_header(category, level=2)

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
                        tqdm.write(f"{category} {colored('✓', 'green')}")
                    else:
                        # Update progress bar color and print question with a red checkmark
                        pbar.colour = "red"
                        tqdm.write(f"{category} {colored('✗', 'red')}")
                else:
                    tqdm.write("Failed to generate a response.")
                
                # Update the progress bar
                pbar.update(1)

    else:
        print("Selected task does not match any known QA checks.")
        sys.exit(1)

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
        report_generator.add_code_block(response["import_statements"], index=6)
        report_generator.add_code_block(response["suggested_code"], index=7)
        
    report_generator.save_report()
    report_generator.open_report()
    print("Completed all checks and generated report.")

if __name__ == "__main__":
    main()
