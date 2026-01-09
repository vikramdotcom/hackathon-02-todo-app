# 🎯 CLI Todo App - Complete Usage Guide

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Main Menu Overview](#main-menu-overview)
3. [Feature Walkthroughs](#feature-walkthroughs)
4. [Tips & Tricks](#tips--tricks)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.13+ (you have Python 3.12.3, which works fine)
- Terminal/Command Prompt

### Launch the Application

```bash
# From the project root directory
python src/main.py
```

### What You'll See

```
=== Todo Application ===

1. Add Todo
2. View All Todos
3. Update Todo
4. Delete Todo
5. Mark Todo Complete
6. Mark Todo Incomplete
7. Filter Todos
8. Session Summary
9. Exit

Enter your choice (1-9): _
```

---

## 📖 Main Menu Overview

| Option | Feature | Description |
|--------|---------|-------------|
| **1** | Add Todo | Create a new todo with title, description, priority, tags, due date, and recurrence |
| **2** | View All Todos | Display all todos in a formatted table |
| **3** | Update Todo | Modify any field of an existing todo |
| **4** | Delete Todo | Remove a todo (with confirmation) |
| **5** | Mark Complete | Mark a todo as completed |
| **6** | Mark Incomplete | Mark a todo as not completed |
| **7** | Filter Todos | Filter by status, priority, or tag |
| **8** | Session Summary | View statistics for current session |
| **9** | Exit | Exit with summary display |

---

## 🎓 Feature Walkthroughs

### 1️⃣ Adding Your First Todo

**Steps:**
1. Select option `1` from main menu
2. Enter the following information:

```
Enter your choice (1-9): 1

--- Add Todo ---

Enter title (required): Buy groceries
Enter description (optional, press Enter to skip): Get milk, eggs, bread, and vegetables
Enter priority (low/medium/high, default: medium): high
Enter tags (comma-separated, optional): shopping, errands, urgent
Enter due date (YYYY-MM-DD or MM/DD/YYYY, optional): 2026-01-15
Enter recurrence pattern (optional, e.g., 'daily', 'weekly'):

✓ Todo created successfully!
  ID: 1
  Title: Buy groceries
  Created: 2026-01-09 19:30:00
```

**Tips:**
- Title is **required** - cannot be empty
- All other fields are **optional** - press Enter to skip
- Priority defaults to "medium" if not specified
- Date formats accepted: `YYYY-MM-DD`, `MM/DD/YYYY`, `MM-DD-YYYY`
- Tags are comma-separated: `work, urgent, project-x`

---

### 2️⃣ Viewing All Todos

**Steps:**
1. Select option `2` from main menu

```
Enter your choice (1-9): 2

=== All Todos (3 total) ===

ID   | Title                          | Status     | Priority | Due Date     | Tags
-------------------------------------------------------------------------------------------------
1    | Buy groceries                  | Pending    | high     | 2026-01-15   | shopping, errands
2    | Write project report           | Completed  | medium   | 2026-01-12   | work
3    | Call dentist                   | Pending    | low      | None         | health

Press Enter to continue...
```

**What You See:**
- **ID**: Unique identifier for each todo
- **Title**: Todo title (truncated if too long)
- **Status**: "Completed" or "Pending"
- **Priority**: low, medium, or high
- **Due Date**: ISO 8601 format or "None"
- **Tags**: Comma-separated list

---

### 3️⃣ Updating a Todo

**Steps:**
1. Select option `3` from main menu
2. Enter the todo ID you want to update
3. Press Enter to keep current values, or type new values

```
Enter your choice (1-9): 3

--- Update Todo ---

Enter todo ID to update: 1

Current todo details:
  ID: 1
  Title: Buy groceries
  Description: Get milk, eggs, bread, and vegetables
  Priority: high
  Tags: shopping, errands, urgent
  Due Date: 2026-01-15
  Recurrence: None

Enter new values (press Enter to keep current value):

  Title [Buy groceries]: Buy groceries and household items
  Description [Get milk, eggs, bread, and vegetables]:
  Priority [high]:
  Tags [shopping, errands, urgent]: shopping, errands, urgent, household
  Due Date [2026-01-15]: 2026-01-16
  Recurrence [None]:

✓ Todo updated successfully!
  ID: 1
  Updated: 2026-01-09 19:35:00
```

**Tips:**
- Only fields you change will be updated
- ID and created_at are **immutable** (cannot be changed)
- Press Enter to keep the current value
- updated_at timestamp is automatically updated

---

### 4️⃣ Deleting a Todo

**Steps:**
1. Select option `4` from main menu
2. Enter the todo ID
3. Confirm deletion

```
Enter your choice (1-9): 4

--- Delete Todo ---

Enter todo ID to delete: 3

Are you sure you want to delete this todo?
  ID: 3
  Title: Call dentist
Confirm (y/n): y

✓ Todo deleted successfully!
  ID: 3
```

**Tips:**
- Deletion requires confirmation (y/n)
- Type `n` or anything other than `y` to cancel
- Deleted IDs are **never reused**
- This action cannot be undone (in-memory only)

---

### 5️⃣ Marking Todos Complete/Incomplete

**Mark Complete:**
```
Enter your choice (1-9): 5

--- Mark Todo Complete ---

Enter todo ID to mark complete: 1

✓ Todo marked as complete!
  ID: 1
  Title: Buy groceries
```

**Mark Incomplete:**
```
Enter your choice (1-9): 6

--- Mark Todo Incomplete ---

Enter todo ID to mark incomplete: 1

✓ Todo marked as incomplete!
  ID: 1
  Title: Buy groceries
```

**Tips:**
- Marking complete/incomplete updates the `updated_at` timestamp
- You can toggle between complete and incomplete as many times as needed
- Completed todos show "Completed" status in the view

---

### 6️⃣ Filtering Todos

**Steps:**
1. Select option `7` from main menu
2. Choose filter type

```
Enter your choice (1-9): 7

=== Filter Todos ===

1. By Status (Completed/Pending/All)
2. By Priority (High/Medium/Low/All)
3. By Tag
4. Back to Main Menu

Enter your choice (1-4):
```

#### Filter by Status
```
Enter your choice (1-4): 1

Select status:
  1. Completed
  2. Pending
  3. All
Enter choice (1-3): 2

=== All Todos (2 total) ===

ID   | Title                          | Status     | Priority | Due Date     | Tags
-------------------------------------------------------------------------------------------------
1    | Buy groceries                  | Pending    | high     | 2026-01-15   | shopping, errands
3    | Call dentist                   | Pending    | low      | None         | health

Press Enter to continue...
```

#### Filter by Priority
```
Enter your choice (1-4): 2

Select priority:
  1. High
  2. Medium
  3. Low
  4. All
Enter choice (1-4): 1

=== All Todos (1 total) ===

ID   | Title                          | Status     | Priority | Due Date     | Tags
-------------------------------------------------------------------------------------------------
1    | Buy groceries                  | Pending    | high     | 2026-01-15   | shopping, errands

Press Enter to continue...
```

#### Filter by Tag
```
Enter your choice (1-4): 3

Enter tag name: shopping

=== All Todos (1 total) ===

ID   | Title                          | Status     | Priority | Due Date     | Tags
-------------------------------------------------------------------------------------------------
1    | Buy groceries                  | Pending    | high     | 2026-01-15   | shopping, errands

Press Enter to continue...
```

**Tips:**
- Filters are case-sensitive for tags
- Empty results show "No todos match the selected filter"
- You can apply multiple filters in sequence
- Select option 4 to return to main menu

---

### 7️⃣ Session Summary

**Steps:**
1. Select option `8` from main menu

```
Enter your choice (1-9): 8

=== Session Summary ===

Total Todos: 5
  - Completed: 2
  - Pending: 3

Operations This Session:
  - Todos Added: 7
  - Todos Updated: 4
  - Todos Deleted: 2
  - Todos Marked Complete: 3

Press Enter to continue...
```

**What It Shows:**
- **Total Todos**: Current number of todos in memory
- **Completed/Pending**: Breakdown by status
- **Operations**: Count of each operation performed this session

**Tips:**
- Counters track all operations since app launch
- Useful for tracking productivity
- Summary is also displayed on exit

---

### 8️⃣ Exiting the Application

**Steps:**
1. Select option `9` from main menu

```
Enter your choice (1-9): 9

=== Session Summary ===

Total Todos: 5
  - Completed: 2
  - Pending: 3

Operations This Session:
  - Todos Added: 7
  - Todos Updated: 4
  - Todos Deleted: 2
  - Todos Marked Complete: 3

Thank you for using Todo Application!
Goodbye!
```

**Important:**
- All data is **lost on exit** (in-memory only)
- Session summary is displayed automatically
- Exit is graceful - no data corruption

---

## 💡 Tips & Tricks

### Input Shortcuts
- **Press Enter** to skip optional fields
- **Empty priority** defaults to "medium"
- **Multiple date formats** accepted (ISO 8601, MM/DD/YYYY, MM-DD-YYYY)
- **Comma-separated tags** with automatic duplicate removal

### Best Practices
1. **Use descriptive titles** - Make them clear and actionable
2. **Set priorities** - Helps with filtering and organization
3. **Add tags** - Makes filtering easier (e.g., "work", "personal", "urgent")
4. **Set due dates** - Track deadlines effectively
5. **Check session summary** - Review your productivity

### Keyboard Shortcuts
- **Ctrl+C** or **Ctrl+D** - Graceful exit (shows summary)
- **Enter** - Continue after viewing todos/summaries

### Common Workflows

**Daily Planning:**
```
1. Launch app
2. Add todos for the day (option 1)
3. Set priorities (high for urgent tasks)
4. Add tags for categorization
5. View all todos (option 2)
6. Mark complete as you finish (option 5)
7. Check summary before exit (option 8)
```

**Weekly Review:**
```
1. Filter by completed (option 7 → 1 → 1)
2. Review what you accomplished
3. Filter by pending (option 7 → 1 → 2)
4. Update priorities for next week
5. Delete outdated todos (option 4)
```

---

## 🔧 Troubleshooting

### Error: "Title is required and cannot be empty"
**Solution:** You must enter a title when adding a todo. Press Enter after typing the title.

### Error: "Priority must be 'low', 'medium', or 'high'"
**Solution:** Enter exactly one of these three values (case-insensitive). Or press Enter for default "medium".

### Error: "Invalid date format"
**Solution:** Use one of these formats:
- `2026-01-15` (ISO 8601)
- `01/15/2026` (MM/DD/YYYY)
- `01-15-2026` (MM-DD-YYYY)

### Error: "Todo with ID X not found"
**Solution:**
- View all todos (option 2) to see valid IDs
- Make sure you're entering a numeric ID
- The todo may have been deleted

### Application Crashes or Freezes
**Solution:**
- Press Ctrl+C to exit gracefully
- Restart the application
- Check Python version: `python --version` (should be 3.12+)

### No Todos Displayed
**Solution:**
- You may have an empty list - add a todo (option 1)
- Check if you're in filter mode - return to main menu
- Restart the application if needed

---

## 📊 Example Session

Here's a complete example session:

```bash
# Launch
python src/main.py

# Add 3 todos
1 → Buy groceries → high → shopping → 2026-01-15
1 → Write report → medium → work → 2026-01-12
1 → Call dentist → low → health → (no date)

# View all
2 → (see 3 todos)

# Mark one complete
5 → 2 (Write report)

# Filter by status
7 → 1 → 1 (View completed)

# Update a todo
3 → 1 → (update title/priority)

# Delete a todo
4 → 3 → y (confirm)

# Session summary
8 → (see statistics)

# Exit
9 → (see final summary)
```

---

## 🎯 Quick Reference Card

| Action | Menu Option | Required Input |
|--------|-------------|----------------|
| Add todo | 1 | Title (required) |
| View all | 2 | None |
| Update | 3 | Todo ID |
| Delete | 4 | Todo ID + confirmation |
| Mark complete | 5 | Todo ID |
| Mark incomplete | 6 | Todo ID |
| Filter | 7 | Filter type + criteria |
| Summary | 8 | None |
| Exit | 9 | None |

---

## 🚀 Ready to Start?

Run this command to launch the application:

```bash
python src/main.py
```

**Enjoy managing your todos!** 📝✨

---

## 📞 Need Help?

- Check the [README.md](../README.md) for project overview
- Review [spec.md](specs/001-phase-1-cli-todo/spec.md) for detailed requirements
- See [quickstart.md](specs/001-phase-1-cli-todo/quickstart.md) for more examples

**Happy task managing!** 🎉
