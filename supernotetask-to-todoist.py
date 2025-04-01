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
import base64
import json

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

def decode_metadata(metadata_base64):
    """Decode Base64 encoded metadata to extract file path and page."""
    if not metadata_base64:
        return "", ""
    
    try:
        # Decode Base64 to bytes, then convert to string
        metadata_json = base64.b64decode(metadata_base64).decode('utf-8')
        
        # Parse JSON
        metadata = json.loads(metadata_json)
        
        # Extract file path and page
        file_path = metadata.get('filePath', '')
        page = metadata.get('page', '')
        
        return file_path, page
    except Exception as e:
        print(f"Warning: Could not decode metadata: {e}")
        return "", ""

def create_todoist_csv(tasks, output_file):
    """Create a CSV file formatted for Todoist import."""
    # Column positions (based on the database structure)
    TASK_ID_POS = 0
    TASK_CONTENT_POS = 3
    DUE_DATE_POS = 5
    STATUS_POS = 8
    REMINDER_DATE_POS = 9
    METADATA_POS = 12  # Base64 encoded metadata
    
    # Todoist CSV headers
    headers = ['TYPE', 'CONTENT', 'DESCRIPTION', 'PRIORITY', 'DATE']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for task in tasks:
                # Get task description (content)
                content = task[TASK_CONTENT_POS] if task[TASK_CONTENT_POS] else "Untitled Task"
                
                # Extract metadata for description
                description = ""
                if len(task) > METADATA_POS and task[METADATA_POS]:
                    file_path, page = decode_metadata(task[METADATA_POS])
                    if file_path:
                        # Extract just the filename from the path
                        file_name = os.path.basename(file_path)
                        description = f"Supernote Source: {file_name}, Page: {page}"
                
                # Get due date
                due_date = ""
                if task[DUE_DATE_POS]:
                    due_date = convert_timestamp_to_date(task[DUE_DATE_POS])
                
                # Get reminder date if due date is empty
                if not due_date and task[REMINDER_DATE_POS]:
                    due_date = convert_timestamp_to_date(task[REMINDER_DATE_POS])
                
                # Write task to CSV - always use priority 1 (lowest)
                writer.writerow({
                    'TYPE': 'task',
                    'CONTENT': content,
                    'DESCRIPTION': description,
                    'PRIORITY': 1,  # Default low priority
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
        
        # Show metadata if available
        if len(first_task) > 12 and first_task[12]:
            file_path, page = decode_metadata(first_task[12])
            print(f"Source: {file_path}")
            print(f"Page: {page}")
    
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
