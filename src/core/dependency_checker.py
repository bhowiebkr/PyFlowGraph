# dependency_checker.py
# System for checking node dependencies and validating package availability

import ast
import sys
import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum


class DependencyStatus(Enum):
    """Status levels for dependency validation."""
    SATISFIED = "satisfied"          # All dependencies available
    OPTIONAL_MISSING = "optional"    # Optional dependencies missing
    REQUIRED_MISSING = "required"    # Required dependencies missing
    UNKNOWN = "unknown"              # Cannot determine status


class DependencyChecker:
    """Checks node dependencies and validates package availability."""
    
    def __init__(self, venv_path: Optional[str] = None):
        """Initialize dependency checker.
        
        Args:
            venv_path: Path to virtual environment for package validation
        """
        self.venv_path = venv_path
        
        # Common import-to-package mappings
        self.import_to_package_map = {
            "cv2": "opencv-python",
            "PIL": "pillow", 
            "Image": "pillow",
            "ImageFilter": "pillow",
            "torch": "torch",
            "torchvision": "torchvision",
            "torchaudio": "torchaudio", 
            "tensorflow": "tensorflow",
            "tf": "tensorflow",
            "keras": "keras",
            "sklearn": "scikit-learn",
            "pd": "pandas",
            "pandas": "pandas",
            "np": "numpy",
            "numpy": "numpy",
            "plt": "matplotlib",
            "matplotlib": "matplotlib",
            "seaborn": "seaborn",
            "requests": "requests",
            "flask": "flask",
            "django": "django",
            "fastapi": "fastapi",
            "streamlit": "streamlit",
            "gradio": "gradio",
            "transformers": "transformers",
            "datasets": "datasets",
            "accelerate": "accelerate",
            "diffusers": "diffusers"
        }
        
        # Cache for package availability checks
        self._package_cache: Dict[str, bool] = {}
    
    def check_node_dependencies(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check dependencies for a node.
        
        Args:
            node_data: Node data containing code and metadata
            
        Returns:
            Dictionary containing dependency status and details
        """
        # Priority 1: Explicit dependencies from metadata
        explicit_deps = node_data.get("dependencies", [])
        optional_deps = node_data.get("optional_dependencies", [])
        
        # Priority 2: Import scanning from code
        scanned_deps = []
        if "code" in node_data and node_data["code"]:
            scanned_deps = self.scan_imports_from_code(node_data["code"])
        
        # Combine all dependencies
        all_required = explicit_deps + scanned_deps
        all_optional = optional_deps
        
        # Remove duplicates while preserving order
        unique_required = list(dict.fromkeys(all_required))
        unique_optional = list(dict.fromkeys(all_optional))
        
        # Validate availability
        required_status = self.validate_package_availability(unique_required)
        optional_status = self.validate_package_availability(unique_optional)
        
        # Determine overall status
        missing_required = [pkg for pkg, available in required_status.items() if not available]
        missing_optional = [pkg for pkg, available in optional_status.items() if not available]
        
        if missing_required:
            overall_status = DependencyStatus.REQUIRED_MISSING
        elif missing_optional:
            overall_status = DependencyStatus.OPTIONAL_MISSING
        else:
            overall_status = DependencyStatus.SATISFIED
        
        return {
            "status": overall_status,
            "required_dependencies": unique_required,
            "optional_dependencies": unique_optional,
            "required_status": required_status,
            "optional_status": optional_status,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "scanned_imports": scanned_deps
        }
    
    def scan_imports_from_code(self, code: str) -> List[str]:
        """Scan Python code for import statements and extract package names.
        
        Args:
            code: Python code to scan
            
        Returns:
            List of required package names
        """
        if not code.strip():
            return []
        
        packages = set()
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Walk the AST looking for import statements
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Regular import: import module
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]  # Get top-level module
                        package = self._resolve_package_name(module_name)
                        if package:
                            packages.add(package)
                
                elif isinstance(node, ast.ImportFrom):
                    # From import: from module import name
                    if node.module:
                        module_name = node.module.split('.')[0]  # Get top-level module
                        package = self._resolve_package_name(module_name)
                        if package:
                            packages.add(package)
        
        except SyntaxError:
            # Code has syntax errors, can't parse imports
            return []
        
        return list(packages)
    
    def _resolve_package_name(self, import_name: str) -> Optional[str]:
        """Resolve import name to package name using mapping.
        
        Args:
            import_name: The name used in import statement
            
        Returns:
            Package name or None if not mappable
        """
        # Check mapping first
        if import_name in self.import_to_package_map:
            return self.import_to_package_map[import_name]
        
        # Skip built-in modules
        builtin_modules = {
            'sys', 'os', 'io', 'json', 're', 'time', 'math', 'random',
            'datetime', 'collections', 'itertools', 'functools', 'pathlib',
            'typing', 'enum', 'dataclasses', 'contextlib', 'threading',
            'multiprocessing', 'asyncio', 'unittest', 'logging', 'warnings'
        }
        
        if import_name in builtin_modules:
            return None
        
        # For unknown modules, assume import name is package name
        return import_name
    
    def validate_package_availability(self, packages: List[str]) -> Dict[str, bool]:
        """Check if packages are available in the current environment.
        
        Args:
            packages: List of package names to check
            
        Returns:
            Dictionary mapping package names to availability status
        """
        results = {}
        
        for package in packages:
            if package in self._package_cache:
                results[package] = self._package_cache[package]
                continue
            
            # Try to import the package
            available = self._is_package_available(package)
            self._package_cache[package] = available
            results[package] = available
        
        return results
    
    def _is_package_available(self, package_name: str) -> bool:
        """Check if a single package is available.
        
        Args:
            package_name: Name of package to check
            
        Returns:
            True if package is available, False otherwise
        """
        try:
            # Try importing the package
            __import__(package_name)
            return True
        except ImportError:
            # Package not available
            return False
    
    def get_dependency_status_icon(self, status: DependencyStatus) -> str:
        """Get icon character for dependency status.
        
        Args:
            status: Dependency status enum
            
        Returns:
            Single character icon for status
        """
        icons = {
            DependencyStatus.SATISFIED: "✓",
            DependencyStatus.OPTIONAL_MISSING: "⚠",
            DependencyStatus.REQUIRED_MISSING: "✗",
            DependencyStatus.UNKNOWN: "?"
        }
        return icons.get(status, "?")
    
    def get_dependency_status_color(self, status: DependencyStatus) -> str:
        """Get color name for dependency status.
        
        Args:
            status: Dependency status enum
            
        Returns:
            Color name for UI styling
        """
        colors = {
            DependencyStatus.SATISFIED: "green",
            DependencyStatus.OPTIONAL_MISSING: "orange", 
            DependencyStatus.REQUIRED_MISSING: "red",
            DependencyStatus.UNKNOWN: "gray"
        }
        return colors.get(status, "gray")
    
    def create_dependency_tooltip(self, dependency_info: Dict[str, Any]) -> str:
        """Create tooltip text for dependency status.
        
        Args:
            dependency_info: Result from check_node_dependencies
            
        Returns:
            Formatted tooltip text
        """
        lines = []
        
        status = dependency_info["status"]
        lines.append(f"Status: {status.value.title()}")
        
        required = dependency_info["required_dependencies"]
        if required:
            lines.append(f"\nRequired: {', '.join(required)}")
            
            missing_required = dependency_info["missing_required"]
            if missing_required:
                lines.append(f"Missing: {', '.join(missing_required)}")
        
        optional = dependency_info["optional_dependencies"]
        if optional:
            lines.append(f"\nOptional: {', '.join(optional)}")
            
            missing_optional = dependency_info["missing_optional"] 
            if missing_optional:
                lines.append(f"Missing: {', '.join(missing_optional)}")
        
        scanned = dependency_info["scanned_imports"]
        if scanned:
            lines.append(f"\nDetected imports: {', '.join(scanned)}")
        
        return "".join(lines)
    
    def clear_cache(self):
        """Clear the package availability cache."""
        self._package_cache.clear()