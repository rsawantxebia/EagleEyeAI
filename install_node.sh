#!/bin/bash
# Quick Node.js installation script for macOS

echo "=========================================="
echo "Node.js Installation for ANPR Frontend"
echo "=========================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed."
    echo "Please install Homebrew first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ Homebrew found"

# Check if Node.js is already installed
if command -v node &> /dev/null; then
    echo "✅ Node.js is already installed"
    node --version
    npm --version
else
    echo "Installing Node.js..."
    brew install node
    
    if [ $? -eq 0 ]; then
        echo "✅ Node.js installed successfully"
    else
        echo "❌ Failed to install Node.js"
        exit 1
    fi
fi

# Verify installation
echo ""
echo "Verifying installation..."
node --version
npm --version

echo ""
echo "=========================================="
echo "✅ Node.js setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Navigate to frontend directory:"
echo "   cd frontend/angular-ui"
echo ""
echo "2. Install Angular dependencies:"
echo "   npm install"
echo ""
echo "3. Start the development server:"
echo "   npm start"
echo ""
