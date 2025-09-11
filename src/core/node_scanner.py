# node_scanner.py
# Scans example files for node definitions and caches them with dependency information

import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Add project root to path for cross-package imports
import sys
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.flow_format import FlowFormatHandler
from src.core.dependency_checker import DependencyChecker, DependencyStatus


class NodeScanner:
    """Scans example files for node definitions and caches dependency information."""
    
    def __init__(self, examples_dir: str = "examples", venv_path: Optional[str] = None):
        """Initialize the node scanner.
        
        Args:
            examples_dir: Directory containing example .md files
            venv_path: Path to virtual environment for dependency checking
        """
        self.examples_dir = examples_dir
        self.venv_path = venv_path
        
        # Cache for parsed nodes and file timestamps
        self.node_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.file_timestamps: Dict[str, float] = {}
        
        # Initialize dependency checker and flow format handler
        self.dependency_checker = DependencyChecker(venv_path)
        self.flow_handler = FlowFormatHandler()
        
        # Ensure examples directory exists
        if not os.path.exists(self.examples_dir):
            os.makedirs(self.examples_dir)
    
    def scan_nodes(self, force_refresh: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Scan all .md files in examples directory for node definitions.
        
        Args:
            force_refresh: If True, ignore cache and rescan all files
            
        Returns:
            Dictionary mapping file paths to lists of node definitions with dependencies
        """
        all_nodes = {}
        
        # Get all .md files in examples directory
        md_files = []
        for root, dirs, files in os.walk(self.examples_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    md_files.append(file_path)
        
        # Process each file
        for file_path in md_files:
            try:
                # Check if file needs to be rescanned
                if self._should_rescan_file(file_path, force_refresh):
                    nodes = self._scan_file(file_path)
                    self.node_cache[file_path] = nodes
                    self.file_timestamps[file_path] = os.path.getmtime(file_path)
                
                # Add cached nodes to results
                if file_path in self.node_cache:
                    all_nodes[file_path] = self.node_cache[file_path]
                    
            except Exception as e:
                # Log error but continue scanning other files
                print(f"Error scanning {file_path}: {e}")
                continue
        
        return all_nodes
    
    def _should_rescan_file(self, file_path: str, force_refresh: bool) -> bool:
        """Check if a file should be rescanned based on modification time.
        
        Args:
            file_path: Path to the file to check
            force_refresh: If True, always rescan
            
        Returns:
            True if file should be rescanned
        """
        if force_refresh:
            return True
        
        if file_path not in self.file_timestamps:
            return True
        
        if not os.path.exists(file_path):
            return False
        
        current_mtime = os.path.getmtime(file_path)
        cached_mtime = self.file_timestamps[file_path]
        
        return current_mtime > cached_mtime
    
    def _scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single .md file for node definitions.
        
        Args:
            file_path: Path to the .md file to scan
            
        Returns:
            List of node definitions with dependency information
        """
        try:
            # Read and parse the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the markdown content
            graph_data = self.flow_handler.markdown_to_data(content)
            
            # Extract nodes and add dependency information
            nodes = []
            for node_data in graph_data.get("nodes", []):
                # Create enhanced node definition
                enhanced_node = self._enhance_node_with_dependencies(node_data, file_path)
                nodes.append(enhanced_node)
            
            return nodes
            
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return []
    
    def _enhance_node_with_dependencies(self, node_data: Dict[str, Any], source_file: str) -> Dict[str, Any]:
        """Enhance node data with dependency information.
        
        Args:
            node_data: Raw node data from markdown file
            source_file: Path to source file
            
        Returns:
            Enhanced node data with dependency information
        """
        # Create a copy to avoid modifying original data
        enhanced_node = node_data.copy()
        
        # Add source file information
        enhanced_node["source_file"] = source_file
        enhanced_node["source_filename"] = os.path.basename(source_file)
        
        # Check dependencies using dependency checker
        dependency_info = self.dependency_checker.check_node_dependencies(node_data)
        
        # Add dependency information to the node
        enhanced_node["dependency_info"] = dependency_info
        enhanced_node["dependency_status"] = dependency_info["status"]
        
        # Add convenience fields for UI
        enhanced_node["has_missing_required"] = bool(dependency_info["missing_required"])
        enhanced_node["has_missing_optional"] = bool(dependency_info["missing_optional"])
        enhanced_node["all_dependencies_satisfied"] = (
            dependency_info["status"] == DependencyStatus.SATISFIED
        )
        
        return enhanced_node
    
    def get_nodes_by_status(self, status: DependencyStatus) -> List[Dict[str, Any]]:
        """Get all nodes with a specific dependency status.
        
        Args:
            status: Dependency status to filter by
            
        Returns:
            List of nodes with the specified status
        """
        all_nodes = self.scan_nodes()
        filtered_nodes = []
        
        for file_path, nodes in all_nodes.items():
            for node in nodes:
                if node.get("dependency_status") == status:
                    filtered_nodes.append(node)
        
        return filtered_nodes
    
    def get_nodes_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all nodes from a specific file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            List of nodes from the specified file
        """
        all_nodes = self.scan_nodes()
        return all_nodes.get(file_path, [])
    
    def search_nodes(self, query: str, include_description: bool = True) -> List[Dict[str, Any]]:
        """Search for nodes by title and optionally description.
        
        Args:
            query: Search query string
            include_description: Whether to search in node descriptions
            
        Returns:
            List of matching nodes
        """
        query_lower = query.lower()
        all_nodes = self.scan_nodes()
        matching_nodes = []
        
        for file_path, nodes in all_nodes.items():
            for node in nodes:
                # Check title
                title = node.get("title", "").lower()
                if query_lower in title:
                    matching_nodes.append(node)
                    continue
                
                # Check description if enabled
                if include_description:
                    description = node.get("description", "").lower()
                    if query_lower in description:
                        matching_nodes.append(node)
        
        return matching_nodes
    
    def get_dependency_summary(self) -> Dict[str, Any]:
        """Get summary of dependency status across all nodes.
        
        Returns:
            Dictionary with dependency statistics
        """
        all_nodes = self.scan_nodes()
        
        total_nodes = 0
        status_counts = {
            DependencyStatus.SATISFIED: 0,
            DependencyStatus.OPTIONAL_MISSING: 0,
            DependencyStatus.REQUIRED_MISSING: 0,
            DependencyStatus.UNKNOWN: 0
        }
        
        all_required_deps = set()
        all_optional_deps = set()
        missing_packages = set()
        
        for file_path, nodes in all_nodes.items():
            for node in nodes:
                total_nodes += 1
                
                status = node.get("dependency_status", DependencyStatus.UNKNOWN)
                status_counts[status] += 1
                
                dep_info = node.get("dependency_info", {})
                all_required_deps.update(dep_info.get("required_dependencies", []))
                all_optional_deps.update(dep_info.get("optional_dependencies", []))
                missing_packages.update(dep_info.get("missing_required", []))
                missing_packages.update(dep_info.get("missing_optional", []))
        
        return {
            "total_nodes": total_nodes,
            "status_counts": status_counts,
            "total_required_packages": len(all_required_deps),
            "total_optional_packages": len(all_optional_deps),
            "total_missing_packages": len(missing_packages),
            "required_dependencies": sorted(list(all_required_deps)),
            "optional_dependencies": sorted(list(all_optional_deps)),
            "missing_packages": sorted(list(missing_packages))
        }
    
    def check_for_updates(self) -> List[str]:
        """Check for files that have been updated since last scan.
        
        Returns:
            List of file paths that have been updated
        """
        updated_files = []
        
        # Check existing files for updates
        for file_path in self.file_timestamps:
            if os.path.exists(file_path):
                if self._should_rescan_file(file_path, False):
                    updated_files.append(file_path)
        
        # Check for new files
        for root, dirs, files in os.walk(self.examples_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    if file_path not in self.file_timestamps:
                        updated_files.append(file_path)
        
        return updated_files
    
    def refresh_cache(self) -> int:
        """Refresh the entire cache by rescanning all files.
        
        Returns:
            Number of files rescanned
        """
        self.node_cache.clear()
        self.file_timestamps.clear()
        self.dependency_checker.clear_cache()
        
        all_nodes = self.scan_nodes(force_refresh=True)
        return len(all_nodes)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the current cache.
        
        Returns:
            Dictionary with cache statistics
        """
        total_nodes = sum(len(nodes) for nodes in self.node_cache.values())
        
        return {
            "cached_files": len(self.node_cache),
            "total_cached_nodes": total_nodes,
            "cache_size_kb": sys.getsizeof(self.node_cache) / 1024,
            "last_scan_time": max(self.file_timestamps.values()) if self.file_timestamps else 0
        }