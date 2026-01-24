#!/bin/bash
echo "📦 Installing SIS Security Scanner..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.8 or higher."
    exit 1
fi

# Install the package
echo "Installing package..."
pip install -e . > /dev/null 2>&1

# Create global wrapper
INSTALL_DIR="/usr/local/bin"
if [ ! -w "$INSTALL_DIR" ]; then
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    echo "📝 Note: Installing to $INSTALL_DIR (add to PATH if needed)"
fi

# Create wrapper script
cat > "$INSTALL_DIR/sis" << 'WRAPPER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")/.." && pwd 2>/dev/null)"
if [ -f "$SCRIPT_DIR/src/sis/cli.py" ]; then
    cd "$SCRIPT_DIR"
    python -m sis.cli "\$@"
else
    # Try to run from current directory
    python -m sis.cli "\$@"
fi
WRAPPER

chmod +x "$INSTALL_DIR/sis"

echo "✅ Installation complete!"
echo ""
echo "🚀 Usage:"
echo "  sis --help"
echo "  sis scan path/to/terraform.tf"
echo "  sis scan ./infrastructure/ --format json"
echo ""
echo "📚 Examples in current directory:"
echo "  ./sis_wrapper scan test_clean.tf"
echo "  ./demo_sis.sh"
