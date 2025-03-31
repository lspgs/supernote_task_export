#!/usr/bin/env python3
"""
SQLite to Todoist Task Converter

This script reads tasks from a SQLite database and creates a CSV file
that can be imported into Todoist.

Usage:
    python sqlite_to_todoist.py /path/to/your/database.db [output_file.csv]

If output_file.csv is not provided, it defaults to 'todoist_import.csv'
in the current directory.
"""

import sqlite3
import csv
import datetime
import os
import sys

def connect_to_db(db_path):
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def get_active_tasks(conn):
    """Get all tasks with 'needsAction' status from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task WHERE status = 'needsAction'")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error querying tasks: {e}")
        sys.exit(1)

def convert_timestamp_to_date(timestamp_ms):
    """Convert Unix timestamp (milliseconds) to a Todoist-compatible date string."""
    if not timestamp_ms:
        return ""
    
    # Convert milliseconds to seconds
    timestamp_sec = timestamp_ms / 1000
    
    # Convert to datetime
    task_date = datetime.datetime.fromtimestamp(timestamp_sec)
    
    # Format according to Todoist expectations (e.g., "Apr 1 2025")
    return task_date.strftime("%b %d %Y")

def map_priority(priority_value):
    """
    Map priority from the database to Todoist's priority system (1-4).
    
    Todoist priority:
    4 = Highest priority (p1 in Todoist)
    3 = High priority (p2 in Todoist)
    2 = Medium priority (p3 in Todoist)
    1 = Low/no priority (p4 in Todoist)
    """
    if not priority_value:
        return 1
    
    try:
        priority = int(priority_value)
        if priority >= 7:
            return 4  # Highest
        elif priority >= 5:
            return 3  # High
        elif priority >= 3:
            return 2  # Medium
        else:
            return 1  # Low
    except (ValueError, TypeError):
        return 1  # Default to low priority

def create_todoist_csv(tasks, output_file):
    """Create a CSV file formatted for Todoist import."""
    # Column positions (based on the database structure)
    TASK_ID_POS = 0
    TASK_CONTENT_POS = 3
    DUE_DATE_POS = 5
    STATUS_POS = 8
    REMINDER_DATE_POS = 9
    PRIORITY_POS = 15  # Using position 15 as potential priority indicator
    
    # Todoist CSV headers
    headers = ['TYPE', 'CONTENT', 'PRIORITY', 'DATE']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for task in tasks:
                # Get task description (content)
                content = task[TASK_CONTENT_POS] if task[TASK_CONTENT_POS] else "Untitled Task"
                
                # Get due date
                due_date = ""
                if task[DUE_DATE_POS]:
                    due_date = convert_timestamp_to_date(task[DUE_DATE_POS])
                
                # Get reminder date if due date is empty
                if not due_date and task[REMINDER_DATE_POS]:
                    due_date = convert_timestamp_to_date(task[REMINDER_DATE_POS])
                
                # Map priority
                priority = 1  # Default to low priority
                if len(task) > PRIORITY_POS and task[PRIORITY_POS] is not None:
                    priority = map_priority(task[PRIORITY_POS])
                
                # Write task to CSV
                writer.writerow({
                    'TYPE': 'task',
                    'CONTENT': content,
                    'PRIORITY': priority,
                    'DATE': due_date
                })
                
        print(f"Successfully created {output_file} with {len(tasks)} tasks.")
    except Exception as e:
        print(f"Error creating CSV file: {e}")
        sys.exit(1)

def main():
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python sqlite_to_todoist.py /path/to/your/database.db [output_file.csv]")
        sys.exit(1)
    
    # Get database path from arguments
    db_path = sys.argv[1]
    
    # Get output file path (default or from arguments)
    output_file = sys.argv[2] if len(sys.argv) > 2 else "todoist_import.csv"
    
    # Connect to database
    conn = connect_to_db(db_path)
    
    # Get active tasks
    tasks = get_active_tasks(conn)
    
    # Show count of tasks found
    print(f"Found {len(tasks)} active tasks.")
    
    # Debug: Show the first task if available
    if tasks and len(tasks) > 0:
        first_task = tasks[0]
        print("\nFirst task found:")
        print(f"ID: {first_task[0]}")
        print(f"Content: {first_task[3]}")
        print(f"Due Date: {first_task[5]}")
        print(f"Status: {first_task[8]}")
    
    # Create CSV file
    create_todoist_csv(tasks, output_file)
    
    # Close database connection
    conn.close()
    
    # Print instructions
    print("\nTo import tasks into Todoist:")
    print("1. Go to Todoist and open the project where you want to import tasks")
    print("2. Click the three dots (⋮) in the top-right corner")
    print("3. Select 'Import from CSV'")
    print(f"4. Select the file '{output_file}'")
    print("5. Follow the on-screen instructions to complete the import")

if __name__ == "__main__":
    main()
