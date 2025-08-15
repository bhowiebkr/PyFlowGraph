# File Organizer Automation

An intelligent file organization system that automatically scans directories, categorizes files by type and properties, applies organizational rules, and provides detailed operation reports. This workflow demonstrates automated file management capabilities including pattern recognition, rule-based categorization, and bulk file operations with comprehensive logging and verification.

The system showcases enterprise-level file management automation where large directories can be systematically organized according to customizable rules, with real-time feedback and detailed reporting. Each component handles a specific aspect of file organization, from initial scanning through intelligent categorization to final organization with comprehensive audit trails.

## Node: Workflow Starter (ID: workflow-starter)

Entry point node that initiates the file organization workflow. This node serves as the master controller, providing a single button to start the entire automation process. It outputs a trigger signal to begin the folder scanning phase and displays workflow status information.

The node includes a large start button and status display area showing the current phase of the organization process. Designed to be the single interaction point for users to begin file organization operations.

### Metadata

```json
{
  "uuid": "workflow-starter",
  "title": "Workflow Starter",
  "pos": [
    -200.0,
    200.0
  ],
  "size": [
    200,
    150
  ],
  "colors": {
    "title": "#dc3545",
    "body": "#c82333"
  },
  "gui_state": {
    "status": "Ready to start"
  }
}
```

### Logic

```python
@node_entry
def start_workflow() -> str:
    print("=== FILE ORGANIZER WORKFLOW STARTED ===")
    print("Initiating automated file organization process...")
    return "workflow_started"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt

widgets['status_label'] = QLabel('Workflow Status:', parent)
layout.addWidget(widgets['status_label'])

widgets['start_btn'] = QPushButton('Start File Organization', parent)
widgets['start_btn'].setMinimumHeight(40)
widgets['start_btn'].setStyleSheet("QPushButton { font-size: 14px; font-weight: bold; }")
widgets['start_btn'].setToolTip('Begin the automated file organization workflow')
layout.addWidget(widgets['start_btn'])

widgets['status_display'] = QTextEdit(parent)
widgets['status_display'].setMaximumHeight(60)
widgets['status_display'].setReadOnly(True)
widgets['status_display'].setPlainText('Ready to start file organization workflow')
layout.addWidget(widgets['status_display'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    status = outputs.get('output_1', 'Unknown')
    if status == "workflow_started":
        widgets['status_display'].setPlainText('Workflow started - scanning folders...')

def set_initial_state(widgets, state):
    widgets['status_display'].setPlainText(state.get('status', 'Ready to start'))
```

## Node: Folder Scanner (ID: folder-scanner)

Scans a specified directory path using os.listdir() and os.path.isfile() to identify all files (excluding subdirectories) in the target folder. Takes a folder path string input and returns a tuple containing both the file list and the folder path for downstream operations. Includes error handling for non-existent directories.

Implements basic file discovery by iterating through directory contents and filtering for files only. Displays up to 10 sample filenames in console output for verification, with count summary for larger directories. No recursive scanning - operates only on the immediate directory level.

Provides both the file list and base path for downstream categorization and organization operations. The GUI includes a folder browser dialog for path selection and displays the selected path in a text field for manual editing if needed. Returns Tuple[List[str], str] where the first element is the file list and the second is the folder path.

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
from typing import List, Tuple

@node_entry
def scan_folder(folder_path: str) -> Tuple[List[str], str]:
    if not folder_path or not os.path.exists(folder_path):
        error_msg = f"Error: Folder '{folder_path}' does not exist or is empty"
        print(error_msg)
        return [], folder_path
    
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
    
    return files, folder_path
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QFileDialog

layout.addWidget(QLabel('Folder to Organize:', parent))
widgets['folder_path'] = QLineEdit(parent)
widgets['folder_path'].setPlaceholderText('Select or enter folder path...')
layout.addWidget(widgets['folder_path'])

widgets['browse_btn'] = QPushButton('Browse Folder', parent)
widgets['browse_btn'].setToolTip('Open folder browser to select directory to organize')
layout.addWidget(widgets['browse_btn'])

widgets['scan_btn'] = QPushButton('Scan Folder', parent)
widgets['scan_btn'].setToolTip('Scan the selected folder for files to organize')
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

class FileCategorizer:
    """Handles file categorization based on extensions."""
    
    def __init__(self):
        self.categories = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c'],
            'Other': []
        }
    
    def categorize_file(self, filename: str) -> str:
        """Categorize a single file by its extension."""
        file_ext = os.path.splitext(filename)[1].lower()
        
        for category, extensions in self.categories.items():
            if file_ext in extensions:
                return category
        
        return 'Other'
    
    def categorize_batch(self, files: List[str]) -> Dict[str, List[str]]:
        """Categorize a list of files."""
        result = {cat: [] for cat in self.categories.keys()}
        
        for file in files:
            category = self.categorize_file(file)
            result[category].append(file)
        
        return result

def print_categorization_summary(categorized_files: Dict[str, List[str]]):
    """Print a summary of categorization results."""
    print("\n=== FILE CATEGORIZATION RESULTS ===")
    for category, file_list in categorized_files.items():
        if file_list:
            print(f"{category}: {len(file_list)} files")
            for file in file_list[:3]:  # Show first 3
                print(f"  - {file}")
            if len(file_list) > 3:
                print(f"  ... and {len(file_list) - 3} more")

@node_entry
def categorize_files(files: List[str]) -> Dict[str, List[str]]:
    categorizer = FileCategorizer()
    result = categorizer.categorize_batch(files)
    print_categorization_summary(result)
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
from typing import Dict, List, Tuple

class FileOrganizer:
    """Handles file organization operations with dry-run support."""
    
    def __init__(self, base_path: str, dry_run: bool = True):
        self.base_path = base_path
        self.dry_run = dry_run
        self.organized_folder = os.path.join(base_path, "Organized_Files")
        self.moved_count = 0
        self.errors = []
    
    def validate_setup(self) -> Tuple[bool, str]:
        """Validate that the setup is ready for file operations."""
        if not self.base_path or not os.path.exists(self.base_path):
            return False, f"Error: Base path '{self.base_path}' does not exist"
        
        if not self.dry_run and not os.path.exists(self.organized_folder):
            return False, f"Error: Organized folder '{self.organized_folder}' does not exist. Run folder creation first."
        
        return True, "Setup validated"
    
    def resolve_filename_conflict(self, dest_path: str) -> str:
        """Resolve filename conflicts by adding numeric suffix."""
        if not os.path.exists(dest_path):
            return dest_path
        
        directory, filename = os.path.split(dest_path)
        base, ext = os.path.splitext(filename)
        counter = 1
        
        while os.path.exists(dest_path):
            new_name = f"{base}_{counter}{ext}"
            dest_path = os.path.join(directory, new_name)
            counter += 1
        
        return dest_path
    
    def move_file(self, file: str, category: str) -> bool:
        """Move a single file to its category folder."""
        source_path = os.path.join(self.base_path, file)
        category_folder = os.path.join(self.organized_folder, category)
        dest_path = os.path.join(category_folder, file)
        
        try:
            if not os.path.exists(source_path):
                self.errors.append(f"File not found: {file}")
                return False
            
            if self.dry_run:
                print(f"Would move: {file} -> {category}/")
            else:
                dest_path = self.resolve_filename_conflict(dest_path)
                shutil.move(source_path, dest_path)
                print(f"Moved: {file} -> {category}/")
            
            self.moved_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error moving {file}: {str(e)}")
            return False
    
    def organize_batch(self, categorized_files: Dict[str, List[str]]) -> str:
        """Organize all files according to their categories."""
        mode = "DRY RUN MODE - NO FILES WILL BE MOVED" if self.dry_run else "ORGANIZING FILES"
        print(f"\n=== {mode} ===")
        
        for category, files in categorized_files.items():
            if not files:
                continue
            
            for file in files:
                self.move_file(file, category)
        
        return self.generate_summary()
    
    def generate_summary(self) -> str:
        """Generate operation summary."""
        action = "would be moved" if self.dry_run else "moved"
        result = f"Successfully {action}: {self.moved_count} files"
        
        if self.errors:
            result += f"\nErrors: {len(self.errors)}"
            for error in self.errors[:5]:  # Show first 5 errors
                result += f"\n  - {error}"
        
        print(f"\n=== ORGANIZATION COMPLETE ===")
        print(result)
        return result

@node_entry
def organize_files(base_path: str, categorized_files: Dict[str, List[str]], dry_run: bool) -> str:
    organizer = FileOrganizer(base_path, dry_run)
    
    is_valid, validation_msg = organizer.validate_setup()
    if not is_valid:
        print(validation_msg)
        return validation_msg
    
    return organizer.organize_batch(categorized_files)
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
widgets['organize_btn'].setToolTip('Click to organize files according to current settings')
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

## Node: Operation Verifier (ID: operation-verifier)

Verifies the completed file organization operation by scanning the organized folders and generating a detailed report. Counts files in each category folder, identifies any remaining files in the source directory, and provides comprehensive operation statistics.

Takes the base_path and operation_result as inputs and performs post-organization verification. Reports on successful moves, remaining files, and any discrepancies between expected and actual organization results. Includes detailed file counts and folder structure validation.

### Metadata

```json
{
  "uuid": "operation-verifier",
  "title": "Operation Verifier",
  "pos": [
    1500.0,
    200.0
  ],
  "size": [
    280,
    250
  ],
  "colors": {
    "title": "#17a2b8",
    "body": "#138496"
  },
  "gui_state": {}
}
```

### Logic

```python
import os
from typing import Dict, List, Tuple

class OrganizationVerifier:
    """Handles verification of file organization operations."""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.organized_folder = os.path.join(base_path, "Organized_Files")
        self.verification_report = []
        self.total_organized = 0
    
    def validate_paths(self) -> Tuple[bool, str]:
        """Validate that required paths exist."""
        if not self.base_path or not os.path.exists(self.base_path):
            return False, f"Error: Base path '{self.base_path}' does not exist"
        
        if not os.path.exists(self.organized_folder):
            return False, "Error: Organized_Files folder not found"
        
        return True, "Paths validated"
    
    def count_category_files(self, category_path: str) -> List[str]:
        """Count files in a category folder."""
        try:
            return [f for f in os.listdir(category_path) 
                   if os.path.isfile(os.path.join(category_path, f))]
        except Exception:
            return []
    
    def scan_organized_folders(self):
        """Scan all category folders and count organized files."""
        try:
            for category in os.listdir(self.organized_folder):
                category_path = os.path.join(self.organized_folder, category)
                if os.path.isdir(category_path):
                    files_in_category = self.count_category_files(category_path)
                    count = len(files_in_category)
                    self.total_organized += count
                    self.verification_report.append(f"{category}: {count} files")
                    print(f"Verified {category}: {count} files")
        except Exception as e:
            raise Exception(f"Error scanning organized folders: {str(e)}")
    
    def scan_remaining_files(self) -> List[str]:
        """Scan for files remaining in the source directory."""
        remaining_files = []
        try:
            for item in os.listdir(self.base_path):
                item_path = os.path.join(self.base_path, item)
                if os.path.isfile(item_path):
                    remaining_files.append(item)
        except Exception as e:
            raise Exception(f"Error scanning remaining files: {str(e)}")
        
        return remaining_files
    
    def generate_report(self, remaining_files: List[str]) -> str:
        """Generate the final verification report."""
        self.verification_report.append(f"\nRemaining in source: {len(remaining_files)} files")
        self.verification_report.append(f"Total organized: {self.total_organized} files")
        
        if remaining_files:
            self.verification_report.append("Remaining files:")
            for file in remaining_files[:5]:
                self.verification_report.append(f"  - {file}")
            if len(remaining_files) > 5:
                self.verification_report.append(f"  ... and {len(remaining_files) - 5} more")
        
        return "\n".join(self.verification_report)
    
    def verify_organization(self) -> str:
        """Perform complete organization verification."""
        print("\n=== VERIFYING ORGANIZATION RESULTS ===")
        
        try:
            self.scan_organized_folders()
            remaining_files = self.scan_remaining_files()
            result = self.generate_report(remaining_files)
            
            print("\n=== VERIFICATION COMPLETE ===")
            print(result)
            return result
            
        except Exception as e:
            error_msg = f"Error during verification: {str(e)}"
            print(error_msg)
            return error_msg

@node_entry
def verify_organization(base_path: str, operation_result: str) -> str:
    verifier = OrganizationVerifier(base_path)
    
    is_valid, validation_msg = verifier.validate_paths()
    if not is_valid:
        return validation_msg
    
    return verifier.verify_organization()
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton

widgets['verify_label'] = QLabel('Organization Verification:', parent)
layout.addWidget(widgets['verify_label'])

widgets['verify_btn'] = QPushButton('Verify Organization', parent)
widgets['verify_btn'].setToolTip('Verify the results of the file organization operation')
layout.addWidget(widgets['verify_btn'])

widgets['verification_display'] = QTextEdit(parent)
widgets['verification_display'].setMinimumHeight(120)
widgets['verification_display'].setReadOnly(True)
widgets['verification_display'].setPlainText('Verification results will appear here...')
layout.addWidget(widgets['verification_display'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    result = outputs.get('output_1', 'No verification data')
    widgets['verification_display'].setPlainText(result)

def set_initial_state(widgets, state):
    pass
```

## Connections

```json
[
  {
    "start_node_uuid": "workflow-starter",
    "start_pin_name": "exec_out",
    "end_node_uuid": "folder-scanner",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "folder-scanner",
    "start_pin_name": "exec_out",
    "end_node_uuid": "file-categorizer",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "folder-scanner",
    "start_pin_name": "output_1",
    "end_node_uuid": "file-categorizer",
    "end_pin_name": "files"
  },
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
    "start_node_uuid": "folder-scanner",
    "start_pin_name": "output_2",
    "end_node_uuid": "folder-creator",
    "end_pin_name": "base_path"
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
  },
  {
    "start_node_uuid": "folder-scanner",
    "start_pin_name": "output_2",
    "end_node_uuid": "file-mover",
    "end_pin_name": "base_path"
  },
  {
    "start_node_uuid": "file-mover",
    "start_pin_name": "exec_out",
    "end_node_uuid": "operation-verifier",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "folder-scanner",
    "start_pin_name": "output_2",
    "end_node_uuid": "operation-verifier",
    "end_pin_name": "base_path"
  },
  {
    "start_node_uuid": "file-mover",
    "start_pin_name": "output_1",
    "end_node_uuid": "operation-verifier",
    "end_pin_name": "operation_result"
  }
]
```
