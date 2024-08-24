import ast
import importlib
import inspect
import os
from tqdm import tqdm
from typing import Dict, List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

from pyqaai.models.models import CodeElement

class SuppressOutput:
    def __enter__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.stdout
        sys.stderr = self.stderr

class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self, function_name: str):
        self.function_name = function_name
        self.calls = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == self.function_name:
            self.calls.append(node)
        elif isinstance(node.func, ast.Attribute) and node.func.attr == self.function_name:
            self.calls.append(node)
        self.generic_visit(node)

class CalleeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.callees = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.callees.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.callees.append(node.func.attr)
        self.generic_visit(node)


class CodeAnalyser:

    def __init__(self):
        self.project_root = self.find_project_root()
        sys.path.append(self.project_root)

    @staticmethod
    def find_project_root(starting_directory: str = None) -> str:
        if starting_directory is None:
            starting_directory = os.getcwd()

        current_directory = starting_directory
        checked_directories = []

        with tqdm(desc="Searching for project root", leave=True) as pbar:
            while True:
                checked_directories.append(current_directory)
                pbar.set_postfix(current_directory=current_directory)
                
                if any(os.path.exists(os.path.join(current_directory, marker)) for marker in ['setup.py', '.git', 'requirements.txt']):
                    pbar.update(len(checked_directories))
                    return current_directory
                
                parent_directory = os.path.dirname(current_directory)
                if parent_directory == current_directory:
                    pbar.update(len(checked_directories))
                    raise FileNotFoundError("Could not find project root.")
                
                pbar.update(1)
                current_directory = parent_directory

    @staticmethod
    def extract_functions_and_classes_from_module(file_path: str) -> Dict[str, CodeElement]:
        with open(file_path, 'r') as file:
            source = file.read()
            tree = ast.parse(source)
        
        functions_classes = {}
        
        def visit_node(node, parent_class=None):
            if isinstance(node, ast.ClassDef):
                name = node.name
                element_type = 'Class'
                code = ast.get_source_segment(source, node)
                lineno = node.lineno
                functions_classes[name] = CodeElement(element_type=element_type, name=name, code=code, lineno=lineno)
                
                # Visit all child nodes with this class as the parent
                for child in ast.iter_child_nodes(node):
                    visit_node(child, parent_class=name)
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                element_type = 'Function'
                if parent_class:
                    name = f"{parent_class}.{node.name}"
                else:
                    name = node.name
                code = ast.get_source_segment(source, node)
                lineno = node.lineno
                functions_classes[name] = CodeElement(element_type=element_type, name=name, code=code, lineno=lineno)
            
            else:
                # For other node types, continue visiting child nodes
                for child in ast.iter_child_nodes(node):
                    visit_node(child, parent_class=parent_class)

        # Start visiting from the root of the AST
        visit_node(tree)

        return functions_classes

    @staticmethod
    def get_imported_modules(file_path: str) -> Tuple[Dict[str, str], List[str]]:
        with open(file_path, 'r') as file:
            source = file.read()
            tree = ast.parse(source)

        imports = {}
        import_statements = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                statement = ast.get_source_segment(source, node)
                import_statements.add(statement)
                
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports[alias.asname or alias.name] = alias.name
                elif isinstance(node, ast.ImportFrom):
                    module = node.module
                    for alias in node.names:
                        imported_name = alias.name
                        full_import_name = f"{module}.{imported_name}"
                        imports[alias.asname or imported_name] = full_import_name

        return imports, list(import_statements)

    def is_project_module(self, module) -> bool:
        module_file = getattr(module, '__file__', None)
        if module_file is not None:
            module_file = os.path.realpath(module_file)
            project_root_abs = os.path.realpath(self.project_root)
            return module_file.startswith(project_root_abs + os.sep)
        return False

    def load_module_from_import(self, import_path: str) -> str:
        try:
            module_path, _, attr_name = import_path.rpartition('.')
            module = importlib.import_module(module_path)
            
            if not self.is_project_module(module):
                return None
            
            if hasattr(module, attr_name):
                attr = getattr(module, attr_name)
                return inspect.getsource(attr)
            else:
                return None
            
        except (ImportError, Exception):
            return None

    def extract_local_imported_functions(self, imported_modules: Dict[str, str]) -> Dict[str, str]:
        local_functions_classes = {}

        with tqdm(total=len(imported_modules), desc="Processing imports", leave=True) as pbar:
            for imported_name, full_import_name in imported_modules.items():
                with SuppressOutput():
                    definition_code = self.load_module_from_import(full_import_name)
                if definition_code:
                    local_functions_classes[full_import_name] = definition_code
                pbar.update(1)
        
        return local_functions_classes

    @staticmethod
    def find_python_files_in_directory(directory: str) -> List[str]:
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    @staticmethod
    def Analyse_file(file_path: str, function_name: str) -> Tuple[str, Dict[str, str]]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                with SuppressOutput():
                    tree = ast.parse(content, filename=file_path)
            
            visitor = FunctionCallVisitor(function_name)
            visitor.visit(tree)
            
            callers = {}
            for call in visitor.calls:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and call in ast.walk(node):
                        caller_name = f"{node.__class__.__name__}:{node.name}"
                        caller_code = ast.get_source_segment(content, node)
                        callers[caller_name] = caller_code
                        break
            
            return file_path, callers
        except Exception:
            return file_path, {} 

    def find_callers_of_function(self, selected_function: str) -> Dict[str, str]:
        python_files = [f for f in self.find_python_files_in_directory(self.project_root) if os.path.isfile(f)]
        caller_methods = {}

        print(f"Searching for callers of the function '{selected_function}'")
        # print(f"Total Python files to process: {len(python_files)}")

        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.Analyse_file, file, selected_function) for file in python_files]
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Analysing files"):
                file_path, result = future.result()
                if isinstance(result, dict):
                    if result:
                        for caller_name, caller_code in result.items():
                            full_caller_name = f"{os.path.relpath(file_path, self.project_root)}:{caller_name}"
                            caller_methods[full_caller_name] = caller_code
                else:
                    print(result)

        print(f"Search complete. Total callers found: {len(caller_methods)}")
        return caller_methods

    def extract_callee_functions(self, file_path: str, selected_function: str) -> Dict[str, str]:
        with open(file_path, 'r') as file:
            content = file.read()
            tree = ast.parse(content)

        callee_visitor = CalleeVisitor()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == selected_function:
                callee_visitor.visit(node)

        callees = {callee: ast.get_source_segment(content, node) 
                   for node in ast.walk(tree) 
                   for callee in callee_visitor.callees 
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == callee}

        return callees
