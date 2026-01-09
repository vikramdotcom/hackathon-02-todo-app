"""
Phase I CLI Todo App - Main Entry Point

This is the main entry point for the todo application.
"""

import sys
from pathlib import Path

# Add project root to Python path to allow imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.session import Session
from src.services.todo_service import TodoManager
from src.cli.menu import MenuHandler


def main():
    """
    Main function to initialize and run the todo application.
    """
    # Initialize session
    session = Session()

    # Initialize TodoManager
    todo_manager = TodoManager(session)

    # Initialize MenuHandler
    menu_handler = MenuHandler(todo_manager)

    # Run the application
    menu_handler.run()


if __name__ == "__main__":
    main()
