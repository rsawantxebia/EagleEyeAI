#!/usr/bin/env python3
"""
Database setup script for EagleEyeAI.
This script initializes the PostgreSQL database and creates all necessary tables.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from src.database import init_db
from utils.logger import logger

# Load environment variables
load_dotenv()

def check_postgres_connection():
    """Check if PostgreSQL is accessible."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/anpr_db"
    )
    
    try:
        # Try to connect to PostgreSQL server (default postgres database)
        server_url = database_url.rsplit('/', 1)[0] + '/postgres'
        engine = create_engine(server_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL server connection successful")
        return True
    except OperationalError as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return False

def create_database():
    """Create the ANPR database if it doesn't exist."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/anpr_db"
    )
    
    # Extract database name
    db_name = database_url.split('/')[-1]
    server_url = database_url.rsplit('/', 1)[0] + '/postgres'
    
    try:
        engine = create_engine(server_url)
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                ),
                {"db_name": db_name}
            )
            
            if result.fetchone() is None:
                # Database doesn't exist, create it
                conn.execute(text("COMMIT"))  # End any transaction
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
        
        return True
    except OperationalError as e:
        logger.error(f"Error creating database: {e}")
        return False

def initialize_tables():
    """Initialize database tables."""
    try:
        init_db()
        logger.info("Database tables initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing tables: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("ANPR Database Setup")
    print("=" * 60)
    
    # Check PostgreSQL connection
    print("\n1. Checking PostgreSQL connection...")
    if not check_postgres_connection():
        print("\n❌ PostgreSQL connection failed!")
        print("\nPlease ensure PostgreSQL is installed and running.")
        print("\nInstallation options:")
        print("  macOS: brew install postgresql@15")
        print("  macOS: brew services start postgresql@15")
        print("\nOr visit: https://www.postgresql.org/download/")
        return False
    
    # Create database
    print("\n2. Creating database...")
    if not create_database():
        print("\n❌ Failed to create database!")
        print("\nPlease check your DATABASE_URL in .env file.")
        return False
    
    # Initialize tables
    print("\n3. Initializing tables...")
    if not initialize_tables():
        print("\n❌ Failed to initialize tables!")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Database setup completed successfully!")
    print("=" * 60)
    print("\nYou can now start the backend server:")
    print("  python3.9 run.py")
    print("\nAPI will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
