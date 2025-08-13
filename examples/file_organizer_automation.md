# File Organizer Automation

An intelligent file organization system that automatically scans directories, categorizes files by type and properties, applies organizational rules, and provides detailed operation reports. This workflow demonstrates automated file management capabilities including pattern recognition, rule-based categorization, and bulk file operations with comprehensive logging and verification.

The system showcases enterprise-level file management automation where large directories can be systematically organized according to customizable rules, with real-time feedback and detailed reporting. Each component handles a specific aspect of file organization, from initial scanning through intelligent categorization to final organization with comprehensive audit trails.

## Node: Folder Scanner (ID: folder-scanner)

Scans a specified directory path using os.listdir() and os.path.isfile() to identify all files (excluding subdirectories) in the target folder. Takes a folder path string input and returns a List[str] containing just the filenames, not full paths. Includes error handling for non-existent directories.

Implements basic file discovery by iterating through directory contents and filtering for files only. Displays up to 10 sample filenames in console output for verification, with count summary for larger directories. No recursive scanning - operates only on the immediate directory level.

Provides the base file list for downstream categorization and organization operations. The GUI includes a folder browser dialog for path selection and displays the selected path in a text field for manual editing if needed.

### Metadata

```json
{
  "uuid": "folder-scanner",
  "title": "Folder Scanner",
  "pos": [
    100.0,
    200.0
  ],
  "size": [
    250,
    182
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "folder_path": ""
  }
}
```

### Logic

```python
import os
from typing import List

@node_entry
def scan_folder(folder_path: str) -> List[str]:
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist")
        return []
    
    files = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            files.append(item)
    
    print(f"Found {len(files)} files in '{folder_path}'")
    for file in files[:10]:  # Show first 10
        print(f"  - {file}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more files")
    
    return files
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QFileDialog

layout.addWidget(QLabel('Folder to Organize:', parent))
widgets['folder_path'] = QLineEdit(parent)
widgets['folder_path'].setPlaceholderText('Select or enter folder path...')
layout.addWidget(widgets['folder_path'])

widgets['browse_btn'] = QPushButton('Browse Folder', parent)
layout.addWidget(widgets['browse_btn'])

widgets['scan_btn'] = QPushButton('Scan Folder', parent)
layout.addWidget(widgets['scan_btn'])

# Connect browse button
def browse_folder():
    folder = QFileDialog.getExistingDirectory(parent, 'Select Folder to Organize')
    if folder:
        widgets['folder_path'].setText(folder)

widgets['browse_btn'].clicked.connect(browse_folder)
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'folder_path': widgets['folder_path'].text()
    }

def set_initial_state(widgets, state):
    widgets['folder_path'].setText(state.get('folder_path', ''))
```


## Node: File Type Categorizer (ID: file-categorizer)

Categorizes files by extension using predefined mappings for Images (.jpg, .png, etc.), Documents (.pdf, .doc, etc.), Spreadsheets (.xls, .csv, etc.), Audio (.mp3, .wav, etc.), Video (.mp4, .avi, etc.), Archives (.zip, .rar, etc.), and Code (.py, .js, etc.). Uses os.path.splitext() to extract file extensions and case-insensitive matching.

Processes List[str] input and returns Dict[str, List[str]] where keys are category names and values are lists of filenames belonging to each category. Files with unrecognized extensions are placed in an 'Other' category. Extension matching is exact - no fuzzy matching or MIME type detection.

Provides categorization statistics in console output showing file counts per category and sample filenames. Categories with zero files are included in the output dictionary but remain empty lists.

### Metadata

```json
{
  "uuid": "file-categorizer",
  "title": "File Type Categorizer",
  "pos": [
    450.0,
    150.0
  ],
  "size": [
    250,
    118
  ],
  "colors": {
    "title": "#28a745",
    "body": "#1e7e34"
  },
  "gui_state": {}
}
```

### Logic

```python
import os
from typing import Dict, List

@node_entry
def categorize_files(files: List[str]) -> Dict[str, List[str]]:
    categories = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c'],
        'Other': []
    }
    
    result = {cat: [] for cat in categories.keys()}
    
    for file in files:
        file_ext = os.path.splitext(file)[1].lower()
        categorized = False
        
        for category, extensions in categories.items():
            if file_ext in extensions:
                result[category].append(file)
                categorized = True
                break
        
        if not categorized:
            result['Other'].append(file)
    
    # Print summary
    print("\n=== FILE CATEGORIZATION RESULTS ===")
    for category, file_list in result.items():
        if file_list:
            print(f"{category}: {len(file_list)} files")
            for file in file_list[:3]:  # Show first 3
                print(f"  - {file}")
            if len(file_list) > 3:
                print(f"  ... and {len(file_list) - 3} more")
    
    return result
```


## Node: Folder Structure Creator (ID: folder-creator)

Creates directory structure for file organization by creating an 'Organized_Files' folder in the base path, then creating subfolders for each non-empty category. Uses os.makedirs() with existence checking to avoid errors when folders already exist.

Takes base_path string and categorized_files Dict[str, List[str]] as inputs. Only creates subfolders for categories that contain files - empty categories are skipped. Returns status string indicating success or failure with folder creation count.

Includes error handling for permission issues and invalid paths. Console output shows each folder creation action. The organized folder structure becomes the target for the subsequent file moving operations.

### Metadata

```json
{
  "uuid": "folder-creator",
  "title": "Folder Structure Creator",
  "pos": [
    820.0,
    200.0
  ],
  "size": [
    250,
    143
  ],
  "colors": {
    "title": "#fd7e14",
    "body": "#e8590c"
  },
  "gui_state": {}
}
```

### Logic

```python
import os
from typing import Dict, List

@node_entry
def create_folders(base_path: str, categorized_files: Dict[str, List[str]]) -> str:
    if not os.path.exists(base_path):
        return f"Error: Base path '{base_path}' does not exist"
    
    organized_folder = os.path.join(base_path, "Organized_Files")
    
    try:
        # Create main organized folder
        if not os.path.exists(organized_folder):
            os.makedirs(organized_folder)
            print(f"Created main folder: {organized_folder}")
        
        # Create subfolders for each category
        created_folders = []
        for category, files in categorized_files.items():
            if files:  # Only create folder if there are files
                category_folder = os.path.join(organized_folder, category)
                if not os.path.exists(category_folder):
                    os.makedirs(category_folder)
                    created_folders.append(category)
                    print(f"Created subfolder: {category}")
        
        result = f"Successfully created organized structure with {len(created_folders)} categories"
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"Error creating folders: {str(e)}"
        print(error_msg)
        return error_msg
```


## Node: File Organizer & Mover (ID: file-mover)

Moves files from the source directory to categorized subfolders within the 'Organized_Files' directory using shutil.move(). Implements dry-run mode for safe preview without actual file operations. Handles filename conflicts by appending numeric suffixes (_1, _2, etc.) to duplicate names.

Processes base_path, categorized_files dictionary, and dry_run boolean flag. In dry-run mode, only prints intended actions without moving files. In live mode, performs actual file moves with error handling for missing files and permission issues. Returns summary string with move counts and any errors encountered.

Includes GUI checkbox for dry-run toggle and text area for displaying operation results. Error handling captures and reports up to 5 specific error messages. File operations are performed sequentially with individual error isolation to prevent batch failures.

### Metadata

```json
{
  "uuid": "file-mover",
  "title": "File Organizer & Mover",
  "pos": [
    1170.0,
    150.0
  ],
  "size": [
    276,
    418
  ],
  "colors": {
    "title": "#6c757d",
    "body": "#545b62"
  },
  "gui_state": {
    "dry_run": true
  }
}
```

### Logic

```python
import os
import shutil
from typing import Dict, List

@node_entry
def organize_files(base_path: str, categorized_files: Dict[str, List[str]], dry_run: bool) -> str:
    organized_folder = os.path.join(base_path, "Organized_Files")
    
    if dry_run:
        print("\n=== DRY RUN MODE - NO FILES WILL BE MOVED ===")
    else:
        print("\n=== ORGANIZING FILES ===")
    
    moved_count = 0
    errors = []
    
    for category, files in categorized_files.items():
        if not files:
            continue
            
        category_folder = os.path.join(organized_folder, category)
        
        for file in files:
            source_path = os.path.join(base_path, file)
            dest_path = os.path.join(category_folder, file)
            
            try:
                if os.path.exists(source_path):
                    if dry_run:
                        print(f"Would move: {file} -> {category}/")
                    else:
                        # Handle file name conflicts
                        if os.path.exists(dest_path):
                            base, ext = os.path.splitext(file)
                            counter = 1
                            while os.path.exists(dest_path):
                                new_name = f"{base}_{counter}{ext}"
                                dest_path = os.path.join(category_folder, new_name)
                                counter += 1
                        
                        shutil.move(source_path, dest_path)
                        print(f"Moved: {file} -> {category}/")
                    
                    moved_count += 1
                else:
                    errors.append(f"File not found: {file}")
                    
            except Exception as e:
                errors.append(f"Error moving {file}: {str(e)}")
    
    # Summary
    action = "would be moved" if dry_run else "moved"
    result = f"Successfully {action}: {moved_count} files"
    if errors:
        result += f"\nErrors: {len(errors)}"
        for error in errors[:5]:  # Show first 5 errors
            result += f"\n  - {error}"
    
    print(f"\n=== ORGANIZATION COMPLETE ===")
    print(result)
    return result
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QCheckBox, QPushButton, QTextEdit
from PySide6.QtCore import Qt

widgets['dry_run'] = QCheckBox('Dry Run (Preview Only)', parent)
widgets['dry_run'].setChecked(True)
widgets['dry_run'].setToolTip('Check this to preview changes without actually moving files')
layout.addWidget(widgets['dry_run'])

widgets['organize_btn'] = QPushButton('Start Organization', parent)
layout.addWidget(widgets['organize_btn'])

widgets['result_display'] = QTextEdit(parent)
widgets['result_display'].setMinimumHeight(150)
widgets['result_display'].setReadOnly(True)
widgets['result_display'].setPlainText('Click "Start Organization" to begin...')
layout.addWidget(widgets['result_display'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'dry_run': widgets['dry_run'].isChecked()
    }

def set_values(widgets, outputs):
    result = outputs.get('output_1', 'No result')
    widgets['result_display'].setPlainText(result)

def set_initial_state(widgets, state):
    widgets['dry_run'].setChecked(state.get('dry_run', True))
```


## Connections

```json
[
  {
    "start_node_uuid": "file-categorizer",
    "start_pin_name": "exec_out",
    "end_node_uuid": "folder-creator",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "file-categorizer",
    "start_pin_name": "output_1",
    "end_node_uuid": "folder-creator",
    "end_pin_name": "categorized_files"
  },
  {
    "start_node_uuid": "folder-creator",
    "start_pin_name": "exec_out",
    "end_node_uuid": "file-mover",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "file-categorizer",
    "start_pin_name": "output_1",
    "end_node_uuid": "file-mover",
    "end_pin_name": "categorized_files"
  }
]
```
