SYSTEM_PROMPT = (
    "Automated Python Quality Assurance Checking Tool v2.0\n\n",
    "You are a python expert that has been tasked with reviewing a Python function or class.",
    "You will have access to the Function or Class to check, Import Statements, Locally Imported Functions/Classes, and Caller Methods.\n\n",
    "------\n"
    "QA Checks to perform (complete the following FULL JSON list[dict] as instructed and return): {filled_structure}\n\n",
    "DO NOT DEVIATE FROM THE list[dict] structure or add any new keys. Only fill in the values for each check.\n\n",
)

SYSTEM_PROMPT_IMPROVEMENT = (
    "Automated Python Quality Assurance Report Code Improvement Suggestion v2.0\n\n",
    "You are a python expert that has been tasked with reviewing a Python function or class.",
    "You will have access to the Function or Class to check, Import Statements, Locally Imported Functions/Classes, and Caller Methods.\n\n",
    "------\n",
    "You have previously performed the check. Based on the following QA Results, please suggest improvements to the code block provided below based on those results:\n\n",
    "QA Check Results {qa_results}\n\n",
    "You MUST return in the following JSON structure: {{'suggested_code': 'python code here - Original updated function ONLY. Do not include imports or surrounding code unless changes are there too', 'changelog': 'summary of changes in markdown'}}\n\n",
)

QA_PROMPTS = {
    "Tier 1": {
        "Functionality": [
            "Does the function correctly implement its intended behavior, including correct and expected output format and structure?",
        ],
        "Bugs and Edge Cases": [
            "Are there any bugs that have been overlooked? and Have all possible code paths, including rarely executed branches, been reviewed to identify potential bugs? Have edge cases been considered?",
        ],
        "Type Safety": [
            "Are there any potential type-related issues or mismatches?",
        ],
        "Exception Management": [
            "How are exceptions managed? Are they specific and handled properly? or perhaps handled in callers (excluding any tests)?",
        ],
        "Security Considerations": [
            "Are there any security considerations for this function, such as input validation or handling sensitive data?",
        ],
        "Code Integration": [
            "Does this function integrate with the surrounding code and overall codebase well? Is the function compatible with existing systems, considering interface contracts? Are there any potential side effects or unintended consequences of this function that haven't been addressed?",
        ],
    },
    "Tier 2": {
        "Code Style and Readability": [
            "Does the code follow PEP 8 guidelines? Are type and return hints used correctly, appropriately and consistently?",
        ],
        "Testing": [
            "Have there been any tests found? What is the coverage and can it be improved/increased? Are there any barriers to effective testing, such as tight coupling or hidden dependencies?",
        ],
        "Logic Clarity": [
            "Is the logic clear and concise? Are there opportunities to simplify complex logic, perhaps by breaking it down into smaller, more understandable parts?",   
        ],
        "Performance": [
            "Are there any obvious performance optimizations that can be made?",
        ],
        "Dependencies and Imports": [
            "How does this function interact with its dependencies? Are they necessary and used appropriately?",
        ],
    },
    "Tier 3": {
        "Documentation": [
            "Is there a clear, following of PEP 257? and Are complex or non-obvious parts of the code adequately explained through comments or documentation?",
        ],
        "Maintainability and Extensibility": [
            "Is the code modular and well-structured to support future changes? Does the code follow the open/closed principle?",
        ],
        "Common Pitfalls": [
            "Are there any easy-to-miss errors, typical Python pitfalls, or anti-patterns that need attention?"
        ],
    },
}