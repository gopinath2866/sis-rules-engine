#!/bin/bash

echo "Setting up SIS v1.0.0 CI/CD pipeline..."

# Create directories if they don't exist
mkdir -p .github/workflows
mkdir -p scripts
mkdir -p test-results
mkdir -p docs/compliance

# Create GitHub Actions workflow
cat > .github/workflows/sis-validation.yml << 'EOF'
name: SIS Rules Validation

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      test_type:
        description: 'Test suite to run'
        required: false
        default: 'canonical'
        type: choice
        options:
        - canonical
        - unit
        - all

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/sis-validator
  PYTHON_VERSION: '3.11'

jobs:
  lint:
    name: Code Quality & Linting
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install black flake8 isort mypy pytest
        
    - name: Format Check (Black)
      run: |
        black --check src/ tests/ --diff
        
    - name: Lint (Flake8)
      run: |
        flake8 src/ --max-line-length=88 --extend-ignore=E203,W503
        
    - name: Import Sorting (isort)
      run: |
        isort --check-only --profile black src/ tests/
        
    - name: Type Checking (mypy)
      run: |
        mypy src/ --ignore-missing-imports
        
  test:
    name: Test Suite
    runs-on: ubuntu-latest
    needs: lint
    
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
        
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4
      
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-html
        
    - name: Run Unit Tests
      run: |
        python -m pytest tests/test_engine.py tests/test_api.py \
          -v --junitxml=junit/test-results-${{ matrix.python-version }}.xml \
          --cov=src/sis --cov-report=xml:coverage.xml \
          --cov-report=html:htmlcov/
          
    - name: Run Canonical Suite
      if: github.event_name == 'push' || github.event.inputs.test_type == 'canonical'
      run: |
        python -m pytest tests/ -v \
          --junitxml=junit/canonical-results.xml \
          --tb=short
          
    - name: Upload Test Results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-results-py${{ matrix.python-version }}
        path: |
          junit/
          htmlcov/
          coverage.xml
        retention-days: 30
        
  docker-build:
    name: Build & Test Docker Image
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name != 'pull_request'
    
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract Metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=semver,pattern={{major}}
          type=sha,prefix={{branch}}-,suffix={{sha7}}
          
    - name: Build and Push Docker Image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Test Docker Container
      run: |
        docker run --rm \
          -v $(pwd)/rules:/app/rules \
          -v $(pwd)/tests:/app/tests \
          ${{ env.IMAGE_NAME }}:${{ github.sha }} \
          python -m pytest tests/ -v --tb=short
          
  compliance-report:
    name: Generate Compliance Report
    runs-on: ubuntu-latest
    needs: [test, docker-build]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Install Reporting Tools
      run: |
        pip install jinja2 pygments
        
    - name: Generate Compliance Dashboard
      run: |
        python scripts/generate_compliance.py \
          --rules rules/canonical.json \
          --test-results junit/ \
          --output docs/compliance/
          
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/compliance
        destination_dir: ./compliance
EOF

echo "Created GitHub Actions workflow"

# Create compliance script
cat > scripts/generate_compliance.py << 'EOF'
#!/usr/bin/env python3
"""
Generate compliance dashboard from test results and rules
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse
import jinja2

class ComplianceGenerator:
    def __init__(self, rules_path: Path, test_results_dir: Path):
        self.rules_path = rules_path
        self.test_results_dir = test_results_dir
        self.rules = self._load_rules()
        self.test_results = self._collect_test_results()
        
    def _load_rules(self) -> List[Dict]:
        """Load canonical rules from JSON"""
        with open(self.rules_path) as f:
            return json.load(f)
            
    def _collect_test_results(self) -> Dict[str, Any]:
        """Collect test results from JUnit XML files"""
        results = {}
        
        for xml_file in self.test_results_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                for testcase in root.findall('.//testcase'):
                    test_name = testcase.attrib['name']
                    classname = testcase.attrib.get('classname', '')
                    
                    # Extract rule ID from test name
                    rule_id = None
                    if 'irr_ident' in test_name.lower():
                        rule_id = 'IRR-IDENT'
                    elif 'irr_dec' in test_name.lower():
                        rule_id = 'IRR-DEC'
                    elif 'admin' in test_name.lower():
                        rule_id = 'ADMIN'
                    
                    if rule_id:
                        results[test_name] = {
                            'rule': rule_id,
                            'passed': testcase.find('failure') is None,
                            'time': float(testcase.attrib.get('time', 0)),
                            'classname': classname
                        }
            except ET.ParseError:
                continue
                
        return results
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """Generate compliance dashboard data"""
        # Group results by rule type
        rule_stats = {
            'ADMIN': {'total': 0, 'passed': 0, 'tests': []},
            'IRR-DEC': {'total': 0, 'passed': 0, 'tests': []},
            'IRR-IDENT': {'total': 0, 'passed': 0, 'tests': []}
        }
        
        # Calculate statistics
        for test_name, result in self.test_results.items():
            rule_type = result['rule']
            if rule_type in rule_stats:
                rule_stats[rule_type]['total'] += 1
                if result['passed']:
                    rule_stats[rule_type]['passed'] += 1
                
                rule_stats[rule_type]['tests'].append({
                    'name': test_name,
                    'passed': result['passed'],
                    'duration': result['time']
                })
        
        # Overall statistics
        total_tests = sum(stats['total'] for stats in rule_stats.values())
        total_passed = sum(stats['passed'] for stats in rule_stats.values())
        
        dashboard = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'overall': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_tests - total_passed,
                'compliance_percentage': round((total_passed / total_tests) * 100, 2) if total_tests > 0 else 100
            },
            'rules': [],
            'test_coverage': {}
        }
        
        # Add rule details
        for rule in self.rules:
            rule_type = rule.get('type', 'UNKNOWN')
            stats = rule_stats.get(rule_type, {'total': 0, 'passed': 0})
            
            dashboard['rules'].append({
                'id': rule.get('id', ''),
                'type': rule_type,
                'name': rule.get('name', ''),
                'description': rule.get('description', ''),
                'severity': rule.get('severity', 'MEDIUM'),
                'tests_total': stats['total'],
                'tests_passed': stats['passed'],
                'compliance': round((stats['passed'] / stats['total']) * 100, 2) if stats['total'] > 0 else 100
            })
        
        return dashboard
    
    def render_html(self, dashboard: Dict, output_dir: Path):
        """Render HTML dashboard"""
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SIS v1.0.0 Compliance Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                .card { margin-bottom: 1.5rem; }
                .compliance-badge { font-size: 0.9em; }
                .rule-type-admin { border-left: 4px solid #dc3545; }
                .rule-type-irr-dec { border-left: 4px solid #fd7e14; }
                .rule-type-irr-ident { border-left: 4px solid #20c997; }
                .test-pass { color: #198754; }
                .test-fail { color: #dc3545; }
                .severity-critical { color: #dc3545; font-weight: bold; }
                .severity-high { color: #fd7e14; }
                .severity-medium { color: #ffc107; }
                .severity-low { color: #6c757d; }
            </style>
        </head>
        <body>
            <div class="container-fluid py-4">
                <div class="row mb-4">
                    <div class="col">
                        <h1 class="display-4">
                            <i class="fas fa-shield-alt"></i> SIS v1.0.0 Compliance Dashboard
                        </h1>
                        <p class="lead">Security Isolation Standard Rules Validation</p>
                        <p class="text-muted">
                            <i class="fas fa-clock"></i> Generated: {{ dashboard.generated_at }}
                        </p>
                    </div>
                </div>
                
                <!-- Overall Stats -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card text-white bg-primary">
                            <div class="card-body">
                                <h5 class="card-title">Overall Compliance</h5>
                                <h2 class="display-2">{{ dashboard.overall.compliance_percentage }}%</h2>
                                <p class="card-text">
                                    {{ dashboard.overall.passed }}/{{ dashboard.overall.total_tests }} tests passed
                                </p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-danger">
                            <div class="card-body">
                                <h5 class="card-title">ADMIN Rules</h5>
                                <h3>{{ rule_stats.ADMIN.compliance|default(0) }}%</h3>
                                <p>{{ rule_stats.ADMIN.passed|default(0) }}/{{ rule_stats.ADMIN.total|default(0) }} passed</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-warning">
                            <div class="card-body">
                                <h5 class="card-title">IRR-DEC Rules</h5>
                                <h3>{{ rule_stats.IRR_DEC.compliance|default(0) }}%</h3>
                                <p>{{ rule_stats.IRR_DEC.passed|default(0) }}/{{ rule_stats.IRR_DEC.total|default(0) }} passed</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-success">
                            <div class="card-body">
                                <h5 class="card-title">IRR-IDENT Rules</h5>
                                <h3>{{ rule_stats.IRR_IDENT.compliance|default(0) }}%</h3>
                                <p>{{ rule_stats.IRR_IDENT.passed|default(0) }}/{{ rule_stats.IRR_IDENT.total|default(0) }} passed</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Rules Details -->
                <div class="row">
                    <div class="col">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="mb-0"><i class="fas fa-list-check"></i> Rule Compliance Details</h4>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>Rule ID</th>
                                                <th>Type</th>
                                                <th>Name</th>
                                                <th>Description</th>
                                                <th>Severity</th>
                                                <th>Tests</th>
                                                <th>Compliance</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for rule in dashboard.rules %}
                                            <tr class="rule-type-{{ rule.type|lower|replace('_', '-') }}">
                                                <td><code>{{ rule.id }}</code></td>
                                                <td>
                                                    <span class="badge bg-{{ 'danger' if rule.type == 'ADMIN' else 'warning' if rule.type == 'IRR-DEC' else 'success' }}">
                                                        {{ rule.type }}
                                                    </span>
                                                </td>
                                                <td>{{ rule.name }}</td>
                                                <td>{{ rule.description }}</td>
                                                <td class="severity-{{ rule.severity|lower }}">{{ rule.severity }}</td>
                                                <td>{{ rule.tests_passed }}/{{ rule.tests_total }}</td>
                                                <td>
                                                    <div class="progress" style="height: 20px;">
                                                        <div class="progress-bar {% if rule.compliance == 100 %}bg-success{% else %}bg-warning{% endif %}" 
                                                             style="width: {{ rule.compliance }}%">
                                                            {{ rule.compliance }}%
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>
                                                    {% if rule.compliance == 100 %}
                                                    <span class="badge bg-success"><i class="fas fa-check"></i> Compliant</span>
                                                    {% else %}
                                                    <span class="badge bg-danger"><i class="fas fa-times"></i> Non-compliant</span>
                                                    {% endif %}
                                                </td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Test Details -->
                <div class="row mt-4">
                    <div class="col">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="mb-0"><i class="fas fa-vial"></i> Test Execution Details</h4>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    {% for rule_type, stats in rule_stats.items() %}
                                    <div class="col-md-4 mb-3">
                                        <h5>{{ rule_type }} Tests</h5>
                                        <ul class="list-group">
                                            {% for test in stats.tests %}
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                <span class="{% if test.passed %}test-pass{% else %}test-fail{% endif %}">
                                                    <i class="fas fa-{% if test.passed %}check-circle{% else %}times-circle{% endif %}"></i>
                                                    {{ test.name }}
                                                </span>
                                                <span class="badge bg-secondary rounded-pill">{{ "%.2fs"|format(test.duration) }}</span>
                                            </li>
                                            {% endfor %}
                                        </ul>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Footer -->
                <footer class="mt-5 pt-4 border-top">
                    <div class="row">
                        <div class="col">
                            <p class="text-muted">
                                <small>
                                    <i class="fas fa-info-circle"></i>
                                    SIS v1.0.0 - Security Isolation Standard
                                    | Canonical Test Suite: 26 tests
                                    | Generated by GitHub Actions
                                </small>
                            </p>
                        </div>
                    </div>
                </footer>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        
        # Prepare template data
        rule_stats = {}
        for rule_type in ['ADMIN', 'IRR-DEC', 'IRR-IDENT']:
            stats = next((r for r in dashboard['rules'] if r['type'] == rule_type), None)
            if stats:
                rule_stats[rule_type] = stats
        
        template = jinja2.Template(template_str)
        html_content = template.render(
            dashboard=dashboard,
            rule_stats=rule_stats
        )
        
        # Write HTML file
        output_dir.mkdir(parents=True, exist_ok=True)
        html_path = output_dir / 'index.html'
        html_path.write_text(html_content)
        
        # Write JSON data for API consumption
        json_path = output_dir / 'compliance_data.json'
        with open(json_path, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        print(f"Dashboard generated at: {html_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate SIS compliance dashboard')
    parser.add_argument('--rules', required=True, help='Path to canonical rules JSON')
    parser.add_argument('--test-results', required=True, help='Directory containing JUnit XML results')
    parser.add_argument('--output', default='./docs/compliance', help='Output directory')
    
    args = parser.parse_args()
    
    generator = ComplianceGenerator(
        Path(args.rules),
        Path(args.test_results)
    )
    
    dashboard = generator.generate_dashboard()
    generator.render_html(dashboard, Path(args.output))

if __name__ == '__main__':
    main()
EOF

chmod +x scripts/generate_compliance.py
echo "Created compliance generation script"

# Create run canonical suite script
cat > scripts/run_canonical_suite.py << 'EOF'
#!/usr/bin/env python3
"""
Run the canonical test suite and produce a summary
"""
import subprocess
import json
import sys
from pathlib import Path

def run_canonical_suite():
    """Execute the canonical test suite"""
    print("🚀 Running SIS v1.0.0 Canonical Test Suite...")
    print("=" * 60)
    
    # Run pytest with JUnit output
    result = subprocess.run([
        "pytest", "tests/",
        "-v",
        "--tb=short",
        "--junitxml=test-results/canonical.xml",
        "--json-report",
        "--json-report-file=test-results/report.json"
    ], capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Load and display JSON report
    report_path = Path("test-results/report.json")
    if report_path.exists():
        with open(report_path) as f:
            report = json.load(f)
        
        summary = report.get("summary", {})
        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Total tests: {summary.get('total', 0)}")
        print(f"Passed:      {summary.get('passed', 0)}")
        print(f"Failed:      {summary.get('failed', 0)}")
        print(f"Skipped:     {summary.get('skipped', 0)}")
        print(f"Duration:    {summary.get('duration', 0):.2f} seconds")
        
        # Check if all tests passed
        if summary.get('failed', 0) == 0:
            print("\n✅ ALL TESTS PASSED!")
            return True
        else:
            print("\n❌ SOME TESTS FAILED")
            return False
    else:
        print("\n⚠️  No report generated")
        return False

if __name__ == "__main__":
    # Create test-results directory
    Path("test-results").mkdir(exist_ok=True)
    
    success = run_canonical_suite()
    sys.exit(0 if success else 1)
EOF

chmod +x scripts/run_canonical_suite.py
echo "Created canonical suite runner"

# Create updated pyproject.toml if it doesn't exist
if [ ! -f pyproject.toml ]; then
    cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "sis-engine"
version = "1.0.0"
description = "Security Isolation Standard Rules Engine"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "Apache-2.0"}
authors = [
    {name = "SIS Team", email = "sis@example.com"},
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Security",
    "Topic :: Software Development :: Quality Assurance",
]

dependencies = [
    "pydantic>=2.0.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "python-multipart>=0.0.6",
    "pyyaml>=6.0",
    "jinja2>=3.1.0",
    "requests>=2.31.0",
]

[project.urls]
Homepage = "https://github.com/your-org/sis-rules-engine"
Documentation = "https://your-org.github.io/sis-rules-engine"
Repository = "https://github.com/your-org/sis-rules-engine.git"

[project.scripts]
sis-validate = "sis.main:cli"

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  | \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "canonical: canonical test suite",
    "integration: integration tests",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/test_*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
EOF
    echo "Created pyproject.toml"
else
    echo "pyproject.toml already exists, skipping..."
fi

# Create updated Dockerfile if it doesn't exist
if [ ! -f Dockerfile ]; then
    cat > Dockerfile << 'EOF'
# Multi-stage build for SIS Validator
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY rules/ ./rules/
COPY pyproject.toml README.md ./

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY --from=builder /app /app

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose API port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.sis.api.endpoints:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    echo "Created Dockerfile"
else
    echo "Dockerfile already exists, skipping..."
fi

# Create updated docker-compose.yml if it doesn't exist
if [ ! -f docker-compose.yml ]; then
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  sis-validator:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./rules:/app/rules:ro
      - ./test_vectors:/app/tests/test_vectors:ro
    environment:
      - PYTHONPATH=/app/src
      - LOG_LEVEL=INFO
    command: uvicorn src.sis.api.endpoints:app --host 0.0.0.0 --port 8000 --reload
    
  tests:
    build: .
    depends_on:
      - sis-validator
    volumes:
      - ./tests:/app/tests:ro
      - ./rules:/app/rules:ro
    environment:
      - PYTHONPATH=/app/src
      - SIS_API_URL=http://sis-validator:8000
    command: >
      sh -c "sleep 5 && 
      python -m pytest tests/ -v --junitxml=/app/test-results.xml"
      
  compliance:
    build: .
    volumes:
      - ./scripts:/app/scripts:ro
      - ./rules:/app/rules:ro
      - ./test-results:/app/test-results
      - ./reports:/app/reports
    command: >
      python scripts/generate_compliance.py
        --rules /app/rules/canonical.json
        --test-results /app/test-results
        --output /app/reports
EOF
    echo "Created docker-compose.yml"
else
    echo "docker-compose.yml already exists, skipping..."
fi

# Create README update
cat >> README.md << 'EOF'

## CI/CD Status

| Test Suite | Status |
|------------|--------|
| **Canonical Suite (26 tests)** | ![SIS Canonical](https://github.com/your-org/sis-rules-engine/workflows/SIS%20Rules%20Validation/badge.svg) |
| **Code Quality** | ![Code Quality](https://github.com/your-org/sis-rules-engine/workflows/SIS%20Rules%20Validation/badge.svg?branch=main&event=push) |
| **Compliance Dashboard** | [📊 View Dashboard](https://your-org.github.io/sis-rules-engine/compliance/) |

**Latest Release**: [![GitHub release](https://img.shields.io/github/v/release/your-org/sis-rules-engine)](https://github.com/your-org/sis-rules-engine/releases)
**Docker Image**: [![Docker Pulls](https://img.shields.io/docker/pulls/your-org/sis-validator)](https://ghcr.io/your-org/sis-validator)

## Running Tests Locally

```bash
# Run the canonical test suite
./scripts/run_canonical_suite.py

# Generate compliance report
./scripts/generate_compliance.py --rules rules/canonical.json --test-results junit/ --output docs/compliance/

# Run via docker-compose
docker-compose up --build