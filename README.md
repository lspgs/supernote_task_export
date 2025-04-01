# supernote_task_export

A simple Python script to export tasks from Supernote Supernote SQLite databases to Todoist-compatible CSV format.

## Overview

This tool helps you migrate tasks from Supernote SQLite database files to Todoist by:
- Extracting tasks with "needsAction" status
- Converting task data to Todoist's CSV import format
- Preserving task content, due dates, and priorities

## Requirements

- Python 3.6 or higher
- SQLite3 module (included in Python standard library)

No external dependencies are required!

## Usage

```bash
python supternotetask-to-todoist.py /path/to/your/supernote_task_database.db [output_file.csv]
```

If you don't specify an output file, it will create `todoist_import.csv` in the current directory.

## How to Import into Todoist

1. Go to Todoist and open the project where you want to import tasks
2. Click the three dots (⋮) in the top-right corner
3. Select 'Import from CSV'
4. Select the generated CSV file
5. Follow the on-screen instructions to complete the import

## Troubleshooting

If you're having trouble with the extraction:

1. Use the debugging script to examine your database structure:
   ```bash
   python sqlite_debug.py /path/to/your/database.db
   ```

2. This will show all tables, columns, and sample data to help identify the correct structure.

3. For custom extraction, use the debugging script with extraction options:
   ```bash
   python sqlite_debug.py /path/to/database.db --extract --table TABLE_NAME --status-col STATUS_COLUMN --status-val STATUS_VALUE
   ```

## How It Works

The script:
1. Connects to your Supernote SQLite database
2. Queries for tasks with "needsAction" status 
3. Converts timestamps to Todoist-compatible date formats
4. Maps priority values to Todoist's 1-4 priority system
5. Creates a properly formatted CSV file for import

## Limitations

- Currently extracts only active ("needsAction") tasks
- Does not support transferring attachments, comments, or labels
- Due dates are converted to a basic date format (no time or recurrence)

## License

This script is provided as-is under the MIT license. Feel free to modify and distribute as needed.
