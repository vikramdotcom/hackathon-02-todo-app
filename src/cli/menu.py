"""
CLI menu interface for Phase I CLI Todo App.

This module provides the menu display and handler classes for user interaction.
"""

from typing import List
from src.models.todo import Todo
from src.services.todo_service import TodoManager
from src.cli.validators import validate_id, validate_priority, parse_date, format_date


class MenuDisplay:
    """
    Class for displaying menu and todo information.
    """

    @staticmethod
    def display_main_menu():
        """Display the main menu options."""
        print("\n=== Todo Application ===\n")
        print("1. Add Todo")
        print("2. View All Todos")
        print("3. Update Todo")
        print("4. Delete Todo")
        print("5. Mark Todo Complete")
        print("6. Mark Todo Incomplete")
        print("7. Filter Todos")
        print("8. Session Summary")
        print("9. Exit")
        print()

    @staticmethod
    def display_todos(todos: List[Todo]):
        """
        Display todos in a formatted table.

        Args:
            todos: List of todos to display
        """
        if not todos:
            print("\n=== All Todos (0 total) ===\n")
            print("No todos found. Add your first todo to get started!\n")
            return

        print(f"\n=== All Todos ({len(todos)} total) ===\n")

        # Print table header
        print(f"{'ID':<4} | {'Title':<30} | {'Status':<10} | {'Priority':<8} | {'Due Date':<12} | {'Tags':<20}")
        print("-" * 100)

        # Print each todo
        for todo in todos:
            status = "Completed" if todo.completed else "Pending"
            tags_str = ", ".join(todo.tags) if todo.tags else ""
            due_date_str = format_date(todo.due_date)

            # Truncate long titles
            title = todo.title[:27] + "..." if len(todo.title) > 30 else todo.title
            tags_str = tags_str[:17] + "..." if len(tags_str) > 20 else tags_str

            print(f"{todo.id:<4} | {title:<30} | {status:<10} | {todo.priority:<8} | {due_date_str:<12} | {tags_str:<20}")

        print()

    @staticmethod
    def display_success(message: str):
        """
        Display a success message.

        Args:
            message: Success message to display
        """
        print(f"\n✓ {message}\n")

    @staticmethod
    def display_error(message: str):
        """
        Display an error message.

        Args:
            message: Error message to display
        """
        print(f"\n✗ Error: {message}\n")

    @staticmethod
    def display_filter_menu():
        """Display the filter submenu options."""
        print("\n=== Filter Todos ===\n")
        print("1. By Status (Completed/Pending/All)")
        print("2. By Priority (High/Medium/Low/All)")
        print("3. By Tag")
        print("4. Back to Main Menu")
        print()

    @staticmethod
    def display_session_summary(summary: dict):
        """
        Display session statistics.

        Args:
            summary: Dictionary with session statistics
        """
        print("\n=== Session Summary ===\n")
        print(f"Total Todos: {summary['total_todos']}")
        print(f"  - Completed: {summary['completed_count']}")
        print(f"  - Pending: {summary['pending_count']}")
        print()
        print("Operations This Session:")
        print(f"  - Todos Added: {summary['operations']['added']}")
        print(f"  - Todos Updated: {summary['operations']['updated']}")
        print(f"  - Todos Deleted: {summary['operations']['deleted']}")
        print(f"  - Todos Marked Complete: {summary['operations']['completed']}")
        print()


class MenuHandler:
    """
    Class for handling menu operations and user input.
    """

    def __init__(self, todo_manager: TodoManager):
        """
        Initialize MenuHandler with a TodoManager.

        Args:
            todo_manager: TodoManager instance for operations
        """
        self.todo_manager = todo_manager
        self.display = MenuDisplay()
        self.running = True

    def run(self):
        """Main menu loop."""
        while self.running:
            try:
                self.display.display_main_menu()
                choice = input("Enter your choice (1-9): ").strip()

                if choice == "1":
                    self.handle_add_todo()
                elif choice == "2":
                    self.handle_view_todos()
                elif choice == "3":
                    self.handle_update_todo()
                elif choice == "4":
                    self.handle_delete_todo()
                elif choice == "5":
                    self.handle_mark_complete()
                elif choice == "6":
                    self.handle_mark_incomplete()
                elif choice == "7":
                    self.handle_filter_todos()
                elif choice == "8":
                    self.handle_session_summary()
                elif choice == "9":
                    self.handle_exit()
                else:
                    self.display.display_error("Invalid choice. Please enter a number between 1 and 9.")

            except EOFError:
                # Handle Ctrl+D gracefully
                print("\n")
                self.handle_exit()
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\n")
                self.handle_exit()

    def handle_add_todo(self):
        """Handle adding a new todo."""
        try:
            print("\n--- Add Todo ---\n")

            # Get title (required)
            title = input("Enter title (required): ").strip()
            if not title:
                self.display.display_error("Title is required and cannot be empty")
                return

            # Get description (optional)
            description = input("Enter description (optional, press Enter to skip): ").strip()

            # Get priority (optional, default: medium)
            priority_input = input("Enter priority (low/medium/high, default: medium): ").strip()
            try:
                priority = validate_priority(priority_input)
            except ValueError as e:
                self.display.display_error(str(e))
                return

            # Get tags (optional)
            tags_input = input("Enter tags (comma-separated, optional): ").strip()
            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []
            # Remove duplicates
            tags = list(dict.fromkeys(tags))

            # Get due date (optional)
            due_date_input = input("Enter due date (YYYY-MM-DD or MM/DD/YYYY, optional): ").strip()
            due_date = None
            if due_date_input:
                try:
                    due_date = parse_date(due_date_input)
                except ValueError as e:
                    self.display.display_error(str(e))
                    return

            # Get recurrence (optional)
            recurrence = input("Enter recurrence pattern (optional, e.g., 'daily', 'weekly'): ").strip()
            recurrence = recurrence if recurrence else None

            # Add todo
            todo = self.todo_manager.add_todo(
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=due_date,
                recurrence=recurrence
            )

            self.display.display_success(f"Todo created successfully!\n  ID: {todo.id}\n  Title: {todo.title}\n  Created: {todo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        except ValueError as e:
            self.display.display_error(str(e))

    def handle_view_todos(self):
        """Handle viewing all todos."""
        todos = self.todo_manager.get_all_todos()
        self.display.display_todos(todos)
        input("Press Enter to continue...")

    def handle_update_todo(self):
        """Handle updating a todo."""
        try:
            print("\n--- Update Todo ---\n")

            # Get todo ID
            id_input = input("Enter todo ID to update: ").strip()
            todo_id = validate_id(id_input)

            # Get existing todo
            todo = self.todo_manager.get_todo_by_id(todo_id)

            # Display current values
            print("\nCurrent todo details:")
            print(f"  ID: {todo.id}")
            print(f"  Title: {todo.title}")
            print(f"  Description: {todo.description}")
            print(f"  Priority: {todo.priority}")
            print(f"  Tags: {', '.join(todo.tags) if todo.tags else 'None'}")
            print(f"  Due Date: {format_date(todo.due_date)}")
            print(f"  Recurrence: {todo.recurrence if todo.recurrence else 'None'}")
            print("\nEnter new values (press Enter to keep current value):\n")

            # Get new values
            fields = {}

            title_input = input(f"  Title [{todo.title}]: ").strip()
            if title_input:
                fields["title"] = title_input

            description_input = input(f"  Description [{todo.description}]: ").strip()
            if description_input:
                fields["description"] = description_input

            priority_input = input(f"  Priority [{todo.priority}]: ").strip()
            if priority_input:
                try:
                    fields["priority"] = validate_priority(priority_input)
                except ValueError as e:
                    self.display.display_error(str(e))
                    return

            tags_input = input(f"  Tags [{', '.join(todo.tags) if todo.tags else 'None'}]: ").strip()
            if tags_input:
                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                fields["tags"] = list(dict.fromkeys(tags))

            due_date_input = input(f"  Due Date [{format_date(todo.due_date)}]: ").strip()
            if due_date_input:
                try:
                    fields["due_date"] = parse_date(due_date_input)
                except ValueError as e:
                    self.display.display_error(str(e))
                    return

            recurrence_input = input(f"  Recurrence [{todo.recurrence if todo.recurrence else 'None'}]: ").strip()
            if recurrence_input:
                fields["recurrence"] = recurrence_input

            # Update todo
            if fields:
                self.todo_manager.update_todo(todo_id, **fields)
                self.display.display_success(f"Todo updated successfully!\n  ID: {todo_id}\n  Updated: {todo.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("\nNo changes made.")

        except ValueError as e:
            self.display.display_error(str(e))

    def handle_delete_todo(self):
        """Handle deleting a todo."""
        try:
            print("\n--- Delete Todo ---\n")

            # Get todo ID
            id_input = input("Enter todo ID to delete: ").strip()
            todo_id = validate_id(id_input)

            # Get todo for confirmation
            todo = self.todo_manager.get_todo_by_id(todo_id)

            # Confirm deletion
            print(f"\nAre you sure you want to delete this todo?")
            print(f"  ID: {todo.id}")
            print(f"  Title: {todo.title}")
            confirm = input("Confirm (y/n): ").strip().lower()

            if confirm == "y" or confirm == "yes":
                self.todo_manager.delete_todo(todo_id)
                self.display.display_success(f"Todo deleted successfully!\n  ID: {todo_id}")
            else:
                print("\nDeletion cancelled.")

        except ValueError as e:
            self.display.display_error(str(e))

    def handle_mark_complete(self):
        """Handle marking a todo as complete."""
        try:
            print("\n--- Mark Todo Complete ---\n")

            # Get todo ID
            id_input = input("Enter todo ID to mark complete: ").strip()
            todo_id = validate_id(id_input)

            # Mark complete
            todo = self.todo_manager.mark_complete(todo_id)

            if todo.completed:
                self.display.display_success(f"Todo marked as complete!\n  ID: {todo.id}\n  Title: {todo.title}")
            else:
                print(f"\nℹ Todo is already marked as complete.\n  ID: {todo.id}\n  Title: {todo.title}\n")

        except ValueError as e:
            self.display.display_error(str(e))

    def handle_mark_incomplete(self):
        """Handle marking a todo as incomplete."""
        try:
            print("\n--- Mark Todo Incomplete ---\n")

            # Get todo ID
            id_input = input("Enter todo ID to mark incomplete: ").strip()
            todo_id = validate_id(id_input)

            # Mark incomplete
            todo = self.todo_manager.mark_incomplete(todo_id)

            if not todo.completed:
                self.display.display_success(f"Todo marked as incomplete!\n  ID: {todo.id}\n  Title: {todo.title}")
            else:
                print(f"\nℹ Todo is already marked as incomplete.\n  ID: {todo.id}\n  Title: {todo.title}\n")

        except ValueError as e:
            self.display.display_error(str(e))

    def handle_filter_todos(self):
        """Handle filtering todos."""
        while True:
            try:
                self.display.display_filter_menu()
                choice = input("Enter your choice (1-4): ").strip()

                if choice == "1":
                    self.handle_filter_by_status()
                elif choice == "2":
                    self.handle_filter_by_priority()
                elif choice == "3":
                    self.handle_filter_by_tag()
                elif choice == "4":
                    break
                else:
                    self.display.display_error("Invalid choice. Please enter a number between 1 and 4.")

            except (EOFError, KeyboardInterrupt):
                break

    def handle_filter_by_status(self):
        """Handle filtering by status."""
        print("\nSelect status:")
        print("  1. Completed")
        print("  2. Pending")
        print("  3. All")
        choice = input("Enter choice (1-3): ").strip()

        status_map = {"1": "completed", "2": "pending", "3": "all"}
        status = status_map.get(choice, "all")

        todos = self.todo_manager.filter_by_status(status)

        if not todos:
            print(f"\n=== Filtered Todos (0 matches) ===\n")
            print("No todos match the selected filter.\n")
        else:
            self.display.display_todos(todos)

        input("Press Enter to continue...")

    def handle_filter_by_priority(self):
        """Handle filtering by priority."""
        print("\nSelect priority:")
        print("  1. High")
        print("  2. Medium")
        print("  3. Low")
        print("  4. All")
        choice = input("Enter choice (1-4): ").strip()

        priority_map = {"1": "high", "2": "medium", "3": "low", "4": "all"}
        priority = priority_map.get(choice, "all")

        todos = self.todo_manager.filter_by_priority(priority)

        if not todos:
            print(f"\n=== Filtered Todos (0 matches) ===\n")
            print("No todos match the selected filter.\n")
        else:
            self.display.display_todos(todos)

        input("Press Enter to continue...")

    def handle_filter_by_tag(self):
        """Handle filtering by tag."""
        tag = input("\nEnter tag name: ").strip()

        if not tag:
            self.display.display_error("Tag name cannot be empty")
            return

        todos = self.todo_manager.filter_by_tag(tag)

        if not todos:
            print(f"\n=== Filtered Todos (0 matches) ===\n")
            print("No todos match the selected filter.\n")
        else:
            self.display.display_todos(todos)

        input("Press Enter to continue...")

    def handle_session_summary(self):
        """Handle displaying session summary."""
        summary = self.todo_manager.get_session_summary()
        self.display.display_session_summary(summary)
        input("Press Enter to continue...")

    def handle_exit(self):
        """Handle exiting the application."""
        summary = self.todo_manager.get_session_summary()
        self.display.display_session_summary(summary)
        print("Thank you for using Todo Application!")
        print("Goodbye!\n")
        self.running = False
