#!/bin/bash
echo "🚀 SIS Security Scanner Production Deployment"
echo "============================================="
echo ""

# Check if installed globally
if command -v sis &> /dev/null; then
    echo "✅ SIS is already installed globally"
    sis --version
else
    echo "📦 Installing SIS globally..."
    
    # Create global wrapper
    INSTALL_DIR="/usr/local/bin"
    if [ ! -w "$INSTALL_DIR" ]; then
        INSTALL_DIR="$HOME/.local/bin"
        mkdir -p "$INSTALL_DIR"
        echo "   Note: Installing to $INSTALL_DIR (add to PATH if needed)"
        echo "   Add to ~/.bashrc or ~/.zshrc:"
        echo "     export PATH=\"\$PATH:$INSTALL_DIR\""
    fi
    
    # Create wrapper
    cat > "$INSTALL_DIR/sis" << 'WRAPPER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd 2>/dev/null)"
if [ -f "$SCRIPT_DIR/src/sis/cli.py" ]; then
    cd "$SCRIPT_DIR"
    python -m sis.cli "$@"
else
    # Try system installation
    python -c "import sys; sys.path.insert(0, ''); from sis.cli import main; main()" "$@"
fi
WRAPPER
    
    chmod +x "$INSTALL_DIR/sis"
    echo "✅ Installed to $INSTALL_DIR/sis"
fi

echo ""
echo "📊 Testing installation..."
sis --help

echo ""
echo "🔧 Example usage:"
echo "   sis scan path/to/terraform.tf"
echo "   sis scan ./infrastructure/ --format json"
echo "   sis scan . --severity CRITICAL,HIGH"
echo ""
echo "📚 Documentation:"
echo "   https://github.com/yourusername/sis"
echo ""
echo "✅ Deployment complete!"
