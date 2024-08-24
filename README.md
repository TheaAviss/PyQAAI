# PyQAAI

PyQAAI (Python QA AI) is an AI-driven command-line interface (CLI) tool for performing automated quality assurance on Python code. Powered by OpenAI's language models, PyQAAI provides an easy way to perform a Quality Assurance check, analyse code, generate HTML reports, suggest code improvements and interact with an intelligent assistant to improve code quality.

## Features

- **Automated Code Analysis**: Utilize AI to analyse your Python code for potential issues, best practices, and improvements.
- **Interactive CLI**: Engage with a user-friendly command-line interface for seamless interaction.
- **Report Generation**: Generate detailed HTML reports based on the analysis.
- **Customisation**: Configure your OpenAI credentials and other settings with ease with a built in one-time setup process

## Installation

To install PyQAAI, make sure you have Python 3.10 or higher. You can install the package directly from the repository:

```bash
pip install git+https://github.com/theaaviss/pyqaai.git
```

Or clone the repository and install it manually:

```bash
git clone https://github.com/theaaviss/pyqaai.git
cd pyqaai
pip install .
```

## Usage

After installation, you can start using PyQAAI in any working directory by running the following command in your terminal:

```bash
pyqaai
```

### Initial Setup

The first time you run PyQAAI, you'll need to provide your OpenAI API key:
If the API key is not set, you will be prompted to enter it. The key will be saved in a configuration file for future use.

### Interactive Menu

When you run PyQAAI using the `pyqaai` command, you'll be guided through an intuitive interactive menu system designed to help you analyze your Python code efficiently.

#### 1. **Select a Python File**
   - The tool starts by listing all Python files in the *current working directory*. You'll be prompted to select the file you want to analyze. If no Python files are found, the tool will notify you and exit.

#### 2. **Choose a Function or Class**
   - After selecting a Python file, you will then choose a specific function or class from that file. The tool displays all available functions and classes, allowing you to target your analysis.

#### 3. **Select a Task**
   - Once you've chosen a function or class, the tool will present you with the following task options:
     - **Tier 1: Critical – Essential Checks, Bug Detection, and Security**
     - **Tier 2: Integrity – Testing, Code Quality, and Performance**
     - **Tier 3: Longevity – Documentation, Good Practice, and Maintainability**

   Each tier focuses on different aspects of code quality, ranging from critical issues to best practices for long-term maintenance.

#### 4. **Execution and Feedback**
   - During the analysis, PyQAAI collects various details about the selected function or class, including:
     - **The selected function or class itself**
     - **Import statements and the associated code**
     - **Invoked functions**
     - **Callers of the function or class**
  
   - After selecting a task, the tool will execute the analysis. You will receive real-time feedback as the task runs, including progress updates and whether your code passes or fails the checks. The results are clearly indicated to help you understand areas that need improvement.

#### 5. **HTML Report Generation**
   - Once the analysis is complete, PyQAAI automatically generates an HTML report. This report includes a summary of the analysis, detailed findings, and suggested code improvements. The report is saved for you to review or share.

#### 6. **Repeat or Exit**
   - After completing a task, you can choose to return to the menu to perform additional tasks or exit the tool.

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

## Author

Developed by Thea Aviss.
```

---

This `README.md` provides an overview of the project, installation instructions, usage examples, and other relevant details. It is designed to be informative for users and contributors alike. If you have any additional details or modifications you'd like to include, feel free to let me know!