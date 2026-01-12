#!/bin/bash
# Quick PostgreSQL installation script for macOS

echo "=========================================="
echo "PostgreSQL Installation for EagleEyeAI"
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

# Check if PostgreSQL is already installed
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL is already installed"
    psql --version
    echo ""
    echo "Starting PostgreSQL service..."
    brew services start postgresql@15 2>/dev/null || brew services start postgresql@14 2>/dev/null || brew services start postgresql
else
    echo "Installing PostgreSQL..."
    brew install postgresql@15
    
    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL installed successfully"
    else
        echo "❌ Failed to install PostgreSQL"
        exit 1
    fi
fi

# Start PostgreSQL service
echo ""
echo "Starting PostgreSQL service..."
brew services start postgresql@15 2>/dev/null || brew services start postgresql@14 2>/dev/null || brew services start postgresql

# Wait a moment for service to start
sleep 2

# Check if PostgreSQL is running
if brew services list | grep -q "postgresql.*started"; then
    echo "✅ PostgreSQL service is running"
else
    echo "⚠️  PostgreSQL service might not be running. Try:"
    echo "  brew services start postgresql@15"
fi

# Set up default postgres user (if needed)
echo ""
echo "Setting up database user..."
echo "You may be prompted for your system password"

# Try to create postgres user or set password
psql postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';" 2>/dev/null || \
psql -U $(whoami) -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';" 2>/dev/null || \
echo "Note: You may need to set the postgres password manually:"
echo "  psql postgres -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""

echo ""
echo "=========================================="
echo "✅ PostgreSQL setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run database initialization:"
echo "   python3.9 setup_database.py"
echo ""
echo "2. Start the backend server:"
echo "   python3.9 run.py"
echo ""
