"""Security tests for the Willow Dataset Toolkit."""
import os
import subprocess
import json
import ast
import re
from pathlib import Path
import pytest

# Security test markers
pytestmark = [
    pytest.mark.security,
    pytest.mark.skipif(
        not pytest.config.getoption("--run-security"),
        reason="Security tests only run with --run-security flag"
    )
]

# Define paths
ROOT_DIR = Path(__file__).parent.parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"

# List of potentially dangerous functions
DANGEROUS_FUNCTIONS = [
    'eval', 'exec', 'execfile', 'compile', 'open',
    'os.system', 'subprocess.call', 'subprocess.Popen',
    'pickle.load', 'pickle.loads', 'marshal.load', 'marshal.loads',
    'yaml.load', 'yaml.load_all', 'jsonpickle.decode',
    'shelve.open', 'dill.load', 'dill.loads', 'sqlite3.connect',
    'pickle.Unpickler', 'cPickle.Unpickler'
]

# List of sensitive patterns to check
SENSITIVE_PATTERNS = [
    (r'password\s*=', 'Potential hardcoded password'),
    (r'api[_-]?key\s*=', 'Potential API key exposure'),
    (r'secret[_-]?key\s*=', 'Potential secret key exposure'),
    (r'token\s*=', 'Potential token exposure'),
    (r'pwd\s*=', 'Potential password exposure'),
    (r'passwd\s*=', 'Potential password exposure'),
    (r'pass\s*=', 'Potential password exposure'),
    (r'key\s*=', 'Potential key exposure'),
    (r'credential\s*=', 'Potential credential exposure'),
    (r'connection[_-]?string\s*=', 'Potential connection string exposure')
]

# List of potentially dangerous HTML/JS patterns
DANGEROUS_HTML_JS = [
    ('<script>', 'Potential XSS vulnerability'),
    ('javascript:', 'Potential XSS vulnerability'),
    ('eval\(', 'Use of eval() is dangerous'),
    ('\.innerHTML\s*=', 'Potential XSS vulnerability'),
    ('document\.write\s*\(', 'Potential XSS vulnerability'),
    ('setTimeout\([^,)]+[),]', 'Potential XSS vulnerability'),
    ('setInterval\([^,)]+[),]', 'Potential XSS vulnerability'),
    ('new Function\(', 'Dynamic code evaluation is dangerous')
]

# List of required security headers for web responses
REQUIRED_HEADERS = [
    'Content-Security-Policy',
    'X-Content-Type-Options',
    'X-Frame-Options',
    'X-XSS-Protection',
    'Strict-Transport-Security'
]

def get_python_files():
    """Get all Python files in the scripts directory."""
    return list(SCRIPTS_DIR.rglob("*.py"))

def get_html_files():
    """Get all HTML files in the project."""
    return list(ROOT_DIR.rglob("*.html"))

@pytest.mark.dependency()
def test_dependencies_vulnerabilities():
    """Check for known vulnerabilities in dependencies."""
    if not REQUIREMENTS_FILE.exists():
        pytest.skip("requirements.txt not found")
    
    # Check using safety
    try:
        result = subprocess.run(
            ["safety", "check", "-r", str(REQUIREMENTS_FILE)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("\nVulnerable dependencies found:")
            print(result.stdout)
            
        assert result.returncode == 0, "Vulnerable dependencies found"
        
    except FileNotFoundError:
        pytest.skip("safety not installed. Install with: pip install safety")

@pytest.mark.dependency(depends=["test_dependencies_vulnerabilities"])
def test_dangerous_functions():
    """Check for use of dangerous functions in Python files."""
    issues = []
    
    for filepath in get_python_files():
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Skip test files
        if "test_" in str(filepath):
            continue
            
        for func in DANGEROUS_FUNCTIONS:
            if func in content:
                # Check if it's a false positive (e.g., in comments or strings)
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if func in line and not (
                        line.strip().startswith('#') or  # Comment
                        'import' in line or  # Import statement
                        'def ' in line or   # Function definition
                        '=' in line.split(func)[0]  # Assignment
                    ):
                        issues.append(f"{filepath}:{i} - Use of {func}() detected")
    
    assert not issues, "\n".join(["Potentially dangerous functions found:"] + issues)

@pytest.mark.dependency(depends=["test_dependencies_vulnerabilities"])
def test_sensitive_data_exposure():
    """Check for potential sensitive data exposure."""
    issues = []
    
    for filepath in get_python_files() + get_html_files():
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for pattern, message in SENSITIVE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                # Get line numbers
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip common false positives
                        if any(skip in line.lower() for skip in ['example', 'template', 'replace', 'dummy']):
                            continue
                        issues.append(f"{filepath}:{i} - {message}: {line.strip()}")
    
    assert not issues, "\n".join(["Potential sensitive data exposure found:"] + issues)

@pytest.mark.dependency(depends=["test_dependencies_vulnerabilities"])
def test_xss_vulnerabilities():
    """Check for potential XSS vulnerabilities in HTML/JS code."""
    issues = []
    
    for filepath in get_html_files():
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for pattern, message in DANGEROUS_HTML_JS:
            if re.search(pattern, content, re.IGNORECASE):
                # Get line numbers
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip comments and test files
                        if '<!--' in line or '//' in line or 'test' in str(filepath):
                            continue
                        issues.append(f"{filepath}:{i} - {message}: {line.strip()}")
    
    assert not issues, "\n".join(["Potential XSS vulnerabilities found:"] + issues)

@pytest.mark.dependency(depends=["test_dependencies_vulnerabilities"])
def test_ast_analysis():
    """Perform static code analysis using AST to find security issues."""
    issues = []
    
    for filepath in get_python_files():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
                
            # Check for potentially dangerous AST nodes
            for node in ast.walk(tree):
                # Check for eval() calls
                if isinstance(node, ast.Call) and \
                   isinstance(node.func, ast.Name) and \
                   node.func.id == 'eval':
                    issues.append(f"{filepath}:{node.lineno} - Use of eval() detected")
                    
                # Check for exec() calls
                if isinstance(node, ast.Call) and \
                   isinstance(node.func, ast.Name) and \
                   node.func.id == 'exec':
                    issues.append(f"{filepath}:{node.lineno} - Use of exec() detected")
                    
                # Check for shell=True in subprocess calls
                if (isinstance(node, ast.Call) and 
                    isinstance(node.func, ast.Attribute) and 
                    hasattr(node.func.value, 'id') and 
                    node.func.value.id == 'subprocess' and
                    node.func.attr in ['call', 'Popen', 'run']):
                    
                    for kw in node.keywords:
                        if kw.arg == 'shell' and \
                           isinstance(kw.value, ast.Constant) and \
                           kw.value.value is True:
                            issues.append(
                                f"{filepath}:{node.lineno} - "
                                f"Potential shell injection vulnerability: {ast.unparse(node).strip()}"
                            )
                            
        except (SyntaxError, UnicodeDecodeError) as e:
            issues.append(f"{filepath}:0 - Error parsing file: {str(e)}")
    
    assert not issues, "\n".join(["Potential security issues found:"] + issues)

@pytest.mark.dependency(depends=["test_dependencies_vulnerabilities"])
def test_http_security_headers():
    """Test that required security headers are present in HTTP responses."""
    # This is a placeholder for actual HTTP header testing
    # In a real project, you would make HTTP requests and check the headers
    # For now, we'll just check if the visualization script sets security headers
    
    issues = []
    
    # Check if the visualization script has security headers
    visualize_script = SCRIPTS_DIR / "visualize_analysis.py"
    if visualize_script.exists():
        with open(visualize_script, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for security headers in the Flask app
        if "Flask" in content:
            for header in REQUIRED_HEADERS:
                if f"'{header}'" not in content and f'"{header}"' not in content:
                    issues.append(f"Missing security header: {header}")
    
    assert not issues, "\n".join(issues)

# Add a fixture to clean up any test files
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up any test files created during testing."""
    yield
    
    # Remove any test files
    test_files = [
        "temp_dashboard.html",
        "temp_light.html",
        "temp_dark.html",
        "temp_high_contrast.html"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            os.remove(test_file)
