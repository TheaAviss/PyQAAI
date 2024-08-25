import inquirer
import sys
import os
from typing import List, NamedTuple, Dict, Union
from pyqaai.models.models import CodeElement

class UserInterface:
    @staticmethod
    def select_python_file() -> str:
        py_files = [f for f in os.listdir('.') if f.endswith('.py')]
        
        if not py_files:
            print("No Python files found in the current directory.")
            return None
        
        questions = [
            inquirer.List('file',
                          message="Select the Python file to analyze",
                          choices=py_files,
                         ),
        ]
        answers = inquirer.prompt(questions)
        if answers is None:
            print("No file selected.")
            return None
        return answers['file']

    @staticmethod
    def select_function_or_class(functions_classes: Union[Dict[str, CodeElement], List[str]]) -> str:
        if isinstance(functions_classes, dict):
            choices = [f"{'Class' if element.type == 'Class' else 'Function'}: {name}" 
                       for name, element in functions_classes.items()]
        else:
            choices = [f"Unknown: {name}" for name in functions_classes]
        
        questions = [
            inquirer.List('function_class',
                          message="Select a function or class to view the code",
                          choices=choices,
                         ),
        ]
        answers = inquirer.prompt(questions)
        if answers is None:
            print("No function or class selected.")
            return None
        selected = answers['function_class']
        
        return selected.split(': ')[1].split(' (line ')[0]


    @staticmethod
    def select_task(task_choices: List[str]) -> str:
        questions = [
            inquirer.List('task',
                          message="Select a task to perform on the selected function/class",
                          choices=task_choices,
                         ),
        ]
        task_answer = inquirer.prompt(questions)
        if task_answer is None:
            print("No task selected.")
            return None
        return task_answer['task']