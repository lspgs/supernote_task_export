# Supernote to Todoist Task Export

A simple Python script to export tasks from Supernote Supernote SQLite databases to Todoist-compatible CSV format.

## Overview

This tool helps you migrate tasks from Supernote SQLite database files to Todoist by:
- Extracting tasks with "needsAction" status
- Converting task data to Todoist's CSV import format
- Preserving task content, filename, page and due dates


## Requirements

- Python 3.6 or higher
- SQLite3 module (included in Python standard library)
- Supernote Partner app running on the same machine that is running this script 


## Usage

```bash
python supternotetask-to-todoist.py /path/to/your/supernote_task_database.db [output_file.csv]
```

If you don't specify an output file, it will create `todoist_import.csv` in the current directory.

## How to Import into Todoist

1. Go to Todoist and open the project where you want to import tasks
2. Click the three dots (...) in the top-right corner
3. Select 'Import from CSV'
4. Select the generated CSV file
5. Follow the on-screen instructions to complete the import


## How It Works

The script:
1. Connects to your Supernote SQLite database
2. Queries for tasks with "needsAction" status 
3. Converts timestamps to Todoist-compatible date formats
4. Extracts the Filepath and Page location to the Todoist description
5. Creates a properly formatted CSV file for import

## Limitations

- Currently extracts only active ("needsAction") tasks
- Does not support transferring attachments, comments, or labels
- Due dates are converted to a basic date format (no time or recurrence)

## License

This script is provided as-is under the MIT license. Feel free to modify and distribute as needed.
