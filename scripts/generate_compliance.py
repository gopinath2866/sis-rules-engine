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