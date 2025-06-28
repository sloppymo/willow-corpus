"""Tests for documentation coverage and quality."""
import ast
import inspect
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pytest

# Documentation test markers
pytestmark = [
    pytest.mark.documentation,
    pytest.mark.skipif(
        not pytest.config.getoption("--run-docs"),
        reason="Documentation tests only run with --run-docs flag"
    )
]

# Define paths
ROOT_DIR = Path(__file__).parent.parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
DOCS_DIR = ROOT_DIR / "docs"
README_FILE = ROOT_DIR / "README.md"

# Minimum documentation requirements
MIN_FUNCTION_DOC_LENGTH = 1  # At least one line of description
MIN_CLASS_DOC_LENGTH = 1     # At least one line of description
MIN_MODULE_DOC_LENGTH = 3    # Module should have a proper docstring

# Files/directories to exclude from documentation checks
EXCLUDE_PATTERNS = [
    "*__pycache__*",
    "*test_*.py",
    "*conftest.py",
    "*setup.py"
]

def get_python_files() -> List[Path]:
    """Get all Python files in the scripts directory that should be checked."""
    python_files = []
    
    for filepath in SCRIPTS_DIR.rglob("*.py"):
        # Skip test files and excluded patterns
        if any(fnmatch.fnmatch(str(filepath), pattern) for pattern in EXCLUDE_PATTERNS):
            continue
        python_files.append(filepath)
    
    return python_files

class DocstringAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze docstrings in Python code."""
    
    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.current_file: Optional[Path] = None
        self.current_class: Optional[str] = None
    
    def visit_Module(self, node: ast.Module) -> None:
        """Check module-level docstring."""
        self.check_docstring(node, "module", MIN_MODULE_DOC_LENGTH)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class docstring and remember current class name."""
        old_class = self.current_class
        self.current_class = node.name
        self.check_docstring(node, f"class {node.name}", MIN_CLASS_DOC_LENGTH)
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function/method docstring."""
        # Skip special methods unless they have a docstring
        if node.name.startswith('__') and node.name.endswith('__') and not ast.get_docstring(node):
            return
            
        # Skip test functions
        if node.name.startswith('test_'):
            return
            
        # Skip private methods unless they have a docstring
        if node.name.startswith('_') and not ast.get_docstring(node):
            return
            
        func_type = "method" if self.current_class else "function"
        func_name = f"{self.current_class}.{node.name}" if self.current_class else node.name
        
        self.check_docstring(node, f"{func_type} {func_name}", MIN_FUNCTION_DOC_LENGTH)
        self.check_parameters(node, func_name)
        self.check_return_value(node, func_name)
        self.check_raises_section(node, func_name)
        
        self.generic_visit(node)
    
    def check_docstring(self, node: ast.AST, node_type: str, min_length: int) -> None:
        """Check if a node has a docstring meeting minimum requirements."""
        docstring = ast.get_docstring(node)
        
        if not docstring:
            self.issues.append({
                'type': 'missing_docstring',
                'node': node_type,
                'file': str(self.current_file),
                'line': node.lineno,
                'message': f"Missing docstring for {node_type}"
            })
        elif len(docstring.strip().split('\n')) < min_length:
            self.issues.append({
                'type': 'short_docstring',
                'node': node_type,
                'file': str(self.current_file),
                'line': node.lineno,
                'message': f"Docstring too short for {node_type} (min {min_length} lines required)"
            })
    
    def check_parameters(self, node: ast.FunctionDef, func_name: str) -> None:
        """Check if function parameters are documented."""
        docstring = ast.get_docstring(node)
        if not docstring:
            return
            
        # Get parameter names
        params = [arg.arg for arg in node.args.args]
        if node.args.vararg:
            params.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            params.append(f"**{node.args.kwarg.arg}")
        
        # Check for each parameter in docstring
        for param in params:
            # Skip 'self' parameter in methods
            if param == 'self' and self.current_class:
                continue
                
            # Check for parameter in docstring
            param_pattern = re.compile(rf"\b{re.escape(param)}\s*:\s*[^\n]+")
            if not param_pattern.search(docstring):
                self.issues.append({
                    'type': 'missing_param_doc',
                    'node': func_name,
                    'file': str(self.current_file),
                    'line': node.lineno,
                    'message': f"Missing or incomplete documentation for parameter '{param}' in {func_name}"
                })
    
    def check_return_value(self, node: ast.FunctionDef, func_name: str) -> None:
        """Check if return value is documented for functions that return something."""
        # Skip if the function doesn't have a return statement
        if not any(isinstance(n, ast.Return) for n in ast.walk(node)):
            return
            
        docstring = ast.get_docstring(node)
        if not docstring:
            return
            
        # Check for return documentation
        if not re.search(r'\b[Rr]eturns?:\s*[^\n]+', docstring):
            self.issues.append({
                'type': 'missing_return_doc',
                'node': func_name,
                'file': str(self.current_file),
                'line': node.lineno,
                'message': f"Missing return value documentation in {func_name}"
            })
    
    def check_raises_section(self, node: ast.FunctionDef, func_name: str) -> None:
        """Check if raised exceptions are documented."""
        # Find all raised exceptions
        exceptions = set()
        for n in ast.walk(node):
            if isinstance(n, ast.Raise):
                if isinstance(n.exc, ast.Call) and hasattr(n.exc.func, 'id'):
                    exceptions.add(n.exc.func.id)
                elif hasattr(n.exc, 'id'):
                    exceptions.add(n.exc.id)
        
        if not exceptions:
            return
            
        docstring = ast.get_docstring(node)
        if not docstring:
            return
            
        # Check for each exception in docstring
        for exc in exceptions:
            if not re.search(rf'\b[Rr]aises:\s*\n\s*{re.escape(exc)}\s*:', docstring):
                self.issues.append({
                    'type': 'missing_raises_doc',
                    'node': func_name,
                    'file': str(self.current_file),
                    'line': node.lineno,
                    'message': f"Missing documentation for raised exception '{exc}' in {func_name}"
                })

def format_issue(issue: Dict[str, Any]) -> str:
    """Format an issue as a string."""
    return f"{issue['file']}:{issue['line']}: {issue['type']}: {issue['message']}"

@pytest.fixture(scope="module")
def doc_analysis() -> Dict[Path, List[Dict[str, Any]]]:
    """Analyze documentation in all Python files."""
    analyzer = DocstringAnalyzer()
    
    for filepath in get_python_files():
        analyzer.current_file = filepath
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=str(filepath))
                    analyzer.visit(tree)
                except SyntaxError as e:
                    analyzer.issues.append({
                        'type': 'syntax_error',
                        'node': 'module',
                        'file': str(filepath),
                        'line': e.lineno,
                        'message': f"Syntax error: {e.msg}"
                    })
        except Exception as e:
            analyzer.issues.append({
                'type': 'file_error',
                'node': 'module',
                'file': str(filepath),
                'line': 0,
                'message': f"Error reading file: {str(e)}"
            })
    
    # Group issues by file
    issues_by_file: Dict[Path, List[Dict[str, Any]]] = {}
    for issue in analyzer.issues:
        filepath = Path(issue['file'])
        if filepath not in issues_by_file:
            issues_by_file[filepath] = []
        issues_by_file[filepath].append(issue)
    
    return issues_by_file

def test_module_documentation(doc_analysis: Dict[Path, List[Dict[str, Any]]]) -> None:
    """Test that all modules have proper documentation."""
    missing_module_docs = []
    
    for filepath, issues in doc_analysis.items():
        module_issues = [i for i in issues if i['type'] in ('missing_docstring', 'short_docstring') 
                        and i['node'] == 'module']
        
        if module_issues:
            missing_module_docs.append((filepath, module_issues))
    
    if missing_module_docs:
        error_msg = ["Missing or insufficient module docstrings:"]
        for filepath, issues in missing_module_docs:
            error_msg.append(f"\n{filepath}:")
            for issue in issues:
                error_msg.append(f"  Line {issue['line']}: {issue['message']}")
        
        pytest.fail("\n".join(error_msg))

def test_function_documentation(doc_analysis: Dict[Path, List[Dict[str, Any]]]) -> None:
    """Test that all functions and methods have proper documentation."""
    missing_function_docs = []
    
    for filepath, issues in doc_analysis.items():
        function_issues = [i for i in issues 
                         if i['type'] in ('missing_docstring', 'short_docstring')
                         and i['node'].startswith(('function', 'method'))]
        
        if function_issues:
            missing_function_docs.append((filepath, function_issues))
    
    if missing_function_docs:
        error_msg = ["Missing or insufficient function/method docstrings:"]
        for filepath, issues in missing_function_docs:
            error_msg.append(f"\n{filepath}:")
            for issue in issues:
                error_msg.append(f"  Line {issue['line']}: {issue['message']}")
        
        pytest.fail("\n".join(error_msg))

def test_parameter_documentation(doc_analysis: Dict[Path, List[Dict[str, Any]]]) -> None:
    """Test that all function parameters are documented."""
    missing_param_docs = []
    
    for filepath, issues in doc_analysis.items():
        param_issues = [i for i in issues if i['type'] == 'missing_param_doc']
        
        if param_issues:
            missing_param_docs.append((filepath, param_issues))
    
    if missing_param_docs:
        error_msg = ["Missing or incomplete parameter documentation:"]
        for filepath, issues in missing_param_docs:
            error_msg.append(f"\n{filepath}:")
            for issue in issues:
                error_msg.append(f"  Line {issue['line']}: {issue['message']}")
        
        pytest.fail("\n".join(error_msg))

def test_return_documentation(doc_analysis: Dict[Path, List[Dict[str, Any]]]) -> None:
    """Test that return values are documented for functions that return something."""
    missing_return_docs = []
    
    for filepath, issues in doc_analysis.items():
        return_issues = [i for i in issues if i['type'] == 'missing_return_doc']
        
        if return_issues:
            missing_return_docs.append((filepath, return_issues))
    
    if missing_return_docs:
        error_msg = ["Missing return value documentation:"]
        for filepath, issues in missing_return_docs:
            error_msg.append(f"\n{filepath}:")
            for issue in issues:
                error_msg.append(f"  Line {issue['line']}: {issue['message']}")
        
        pytest.fail("\n".join(error_msg))

def test_exception_documentation(doc_analysis: Dict[Path, List[Dict[str, Any]]]) -> None:
    """Test that raised exceptions are documented."""
    missing_raises_docs = []
    
    for filepath, issues in doc_analysis.items():
        raises_issues = [i for i in issues if i['type'] == 'missing_raises_doc']
        
        if raises_issues:
            missing_raises_docs.append((filepath, raises_issues))
    
    if missing_raises_docs:
        error_msg = ["Missing exception documentation:"]
        for filepath, issues in missing_raises_docs:
            error_msg.append(f"\n{filepath}:")
            for issue in issues:
                error_msg.append(f"  Line {issue['line']}: {issue['message']}")
        
        pytest.fail("\n".join(error_msg))

def test_readme_exists() -> None:
    """Test that README.md exists and is not empty."""
    assert README_FILE.exists(), "README.md does not exist"
    assert README_FILE.stat().st_size > 0, "README.md is empty"

def test_readme_format() -> None:
    """Test that README.md has the required sections."""
    if not README_FILE.exists():
        pytest.skip("README.md not found")
    
    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    required_sections = [
        'installation',
        'usage',
        'features',
        'contributing',
        'license'
    ]
    
    missing_sections = [section for section in required_sections 
                       if f"# {section}" not in content]
    
    assert not missing_sections, f"Missing required sections in README.md: {', '.join(missing_sections)}"

# Add a command-line option to show documentation coverage

def pytest_addoption(parser):
    """Add command-line options for documentation tests."""
    parser.addoption(
        "--run-docs",
        action="store_true",
        default=False,
        help="Run documentation tests"
    )

def pytest_configure(config):
    """Register documentation marker."""
    config.addinivalue_line(
        "markers",
        "documentation: mark test as documentation test"
    )
