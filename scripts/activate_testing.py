#!/usr/bin/env python
"""
Quick activation script for PyFlowGraph Enhanced Testing Infrastructure

Run this script to verify and activate the testing infrastructure for Claude Code.
"""

import os
import sys
from pathlib import Path

def main():
    """Activate and verify PyFlowGraph testing infrastructure."""
    
    print("PyFlowGraph Enhanced Testing Infrastructure")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    
    # Check for required files
    required_files = [
        "pytest.ini",
        "test_runner.py", 
        "test_analyzer.py",
        "test_generator.py",
        ".claude/config.yaml",
        ".claude/project.json",
        "claude_agents/test_analysis_agent.md",
        "claude_commands/test_command.md"
    ]
    
    print("Checking infrastructure files...")
    all_present = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [MISSING] {file_path}")
            all_present = False
    
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    required_deps = ["pytest", "xdist", "pytest_timeout", "pytest_cov"]
    
    for dep in required_deps:
        try:
            __import__(dep)
            print(f"  [OK] {dep}")
        except ImportError:
            print(f"  [MISSING] {dep} - Install with: pip install -r requirements.txt")
            all_present = False
    
    print()
    
    if all_present:
        print("SUCCESS: All infrastructure components are ready!")
        print()
        print("Quick Start Commands:")
        print("  python test_runner.py --fast --format claude")
        print("  python test_analyzer.py --format claude") 
        print("  python test_generator.py --analyze-only")
        print()
        print("Claude Code Commands:")
        print("  /test fast")
        print("  /fix-tests auto")
        print("  /test-health overview")
        print()
        print("Documentation: TESTING_GUIDE.md")
        
    else:
        print("WARNING: Some components are missing. Please install dependencies:")
        print("  pip install -r requirements.txt")
    
    return all_present

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)