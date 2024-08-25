# PyQAAI
```
 _____        ____                      _____ 
|  __ \      / __ \     /\        /\   |_   _|
| |__) |   _| |  | |   /  \      /  \    | |  
|  ___/ | | | |  | |  / /\ \    / /\ \   | |  
| |   | |_| | |__| | / ____ \  / ____ \ _| |_ 
|_|    \__, |\___\_\/_/    \_\/_/    \_\_____|
        __/ |                                 
        |___/     
```
PyQAAI (Python Quality Assurance AI) is a powerful, AI-driven command-line tool designed to automate and elevate the quality assurance process for Python code. It seamlessly integrates comprehensive code analysis through Abstract Syntax Tree (AST) inspections and SoTA LLM Inference, executes a tiered suite of automated QA checks, and generates detailed HTML reports. PyQAAI also offers intelligent code improvement suggestions, serving as a guided assistant to help you maintain high coding standards. 

While this tool is invaluable for identifying potential issues and enhancing your code, it's important to treat its suggestions as potential guidance rather than definitive solutions. Use PyQAAI to catch overlooked details and inspire thoughtful improvements in your Python development projects.

## Features

- **Automated Code Analysis**: Utilises AST and a SoTA LLM to analyse your Python code for potential issues, best practices, and improvements.
- **Interactive CLI**: Engage with a user-friendly command-line interface for seamless interaction.
- **Automatic Code Improvement Suggestions**: Automatic Code Improvement Suggestions for any failing checks.
- **Report Generation**: Generates detailed HTML reports based on the analysis.
- **Configuration**: Add your OpenAI credentials and other settings with ease with a built in one-time setup process
- **Custom Prompt Mode**: Leverage the intelligent assistant and integrated code analysis to perform any custom task.

## Installation

To install PyQAAI, make sure you have Python >=3.10. You can install directly via `pip` [package link](https://pypi.org/project/pyqaai/0.1.6/):

```
pip install pyqaai
```

Or install the package directly from the repository:
```bash
git clone https://github.com/theaaviss/pyqaai.git
cd pyqaai
python3 -m build
pip install .
```

## Usage

After installation, you can start using PyQAAI in any current working directory by running the following command in your terminal:

```bash
pyqaai
```

### Initial Setup

The first time you run PyQAAI, you'll need to provide your OpenAI API key:
If the API key is not set, you will be prompted to enter it. The key will be saved in a configuration file for future use.

### Interactive Menu

When you run PyQAAI using the `pyqaai` command, you'll be guided through an intuitive interactive menu system designed to help you analyse your Python code efficiently.

#### 1. **Select a Python File**
   - The tool starts by listing all Python files in the *current working directory*. You'll be prompted to select the file you want to analyse. If no Python files are found, the tool will notify you and exit.

#### 2. **Choose a Function or Class**
   - After selecting a Python file, you will then choose a specific function or class from that file. The tool displays all available functions and classes, allowing you to target your analysis.

#### 3. **Select a Task**
   - Once you've chosen a function or class, the tool will present you with the following task options:
     - **Tier 1: Critical – Essential Checks, Bug Detection, and Security**
     - **Tier 2: Integrity – Testing, Code Quality, and Performance**
     - **Tier 3: Longevity – Documentation, Good Practice, and Maintainability**
     - **Custom Task: Tailored help via Intelligent Code Assistant**

   Each tier focuses on different aspects of code quality, ranging from critical issues to best practices for long-term maintenance.

#### 4. **Execution and Feedback**
   - During the analysis, PyQAAI collects various details about the selected function or class, including:
     - **The selected function or class itself**
     - **Import statements and the associated code**
     - **Invoked functions**
     - **Callers of the function or class**
  
   - After selecting a task, the tool will execute the analysis. You will receive real-time feedback as the task runs, including progress updates and whether your code passes or fails the checks. The results are clearly indicated to help you understand areas that need improvement.

#### 5. **HTML Report Generation**
   - Once the analysis is complete, PyQAAI automatically generates an HTML report. This report includes a summary of the analysis, detailed findings, and suggested code improvements. The report is saved for you and opened automatically to review or share.

## Dependencies

PyQAAI relies on several Python packages:

- `openai` - OpenAI API client
- `tqdm` - Progress bar library
- `inquirer` - Command-line interface library
- `termcolor` - Colored terminal output
- `requests` - HTTP requests library
- `markdown` - Markdown to HTML converter

These dependencies are automatically installed when you install PyQAAI.

## Contributing

Contributions are welcome! Please submit issues and pull requests via the [GitHub repository](https://github.com/theaaviss/pyqaai).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
