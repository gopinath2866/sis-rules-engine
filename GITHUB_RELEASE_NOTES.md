# SIS Rules Engine v1.0.0

## 🎉 Initial Public Release

A Security and Infrastructure Standards validation engine for Infrastructure as Code (IaC).

### ✨ Features
- **Multi-format Support**: Terraform, CloudFormation, K8s, ARM, Docker Compose
- **Canonical Rule Set**: Pre-built security validation rules  
- **CLI & API**: Multiple interfaces for integration
- **Extensible**: Easy to add custom rules and parsers
- **MIT Licensed**: Open source and free to use

### 🚀 Getting Started
\`\`\`bash
# Clone the repository
git clone https://github.com/gopinath2866/sis-rules-engine.git
cd sis-rules-engine

# Install the package
pip install -e .

# Validate a Terraform file
sis validate terraform-examples/main.tf

# List available rules
sis rules list
\`\`\`

### 📚 Documentation
- [README.md](README.md) - Quick start guide
- [ROADMAP.md](ROADMAP.md) - Future plans
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md) - Usage terms
- [SECURITY-GUARANTEES.md](SECURITY-GUARANTEES.md) - Security information

### 🛠️ Technical Details
- **Python 3.8+** compatible
- **Modular architecture** with clean separation
- **Comprehensive test suite**
- **CI/CD ready** with GitHub Actions

### 📦 What's Included
- Core validation engine
- Multiple parser implementations
- CLI interface
- REST API (beta)
- Example configurations
- Documentation

### 🔧 Quick Example
\`\`\`python
from src.sis.engine import RulesEngine
from src.sis.scanner import Scanner

# Create a scanner and engine
scanner = Scanner()
engine = RulesEngine()

# Scan a directory
results = scanner.scan_directory("terraform-examples/")
print(f"Found {len(results.files)} files")

# Validate against rules
violations = engine.validate(results)
print(f"Found {len(violations)} violations")
\`\`\`

### 📄 License
MIT License - See [LICENSE](LICENSE) file

### 🙏 Acknowledgements
Thanks to all contributors and the open source community.

---

**Next Steps**: Check out [ROADMAP.md](ROADMAP.md) for v1.1.0 plans including Docker images, package distribution, and enhanced rule sets.

**Report Issues**: https://github.com/gopinath2866/sis-rules-engine/issues
