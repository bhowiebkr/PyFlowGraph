@echo off
echo Setting up GitHub labels for bug tracking...

REM Priority Labels
gh label create "critical" --description "Critical priority - system breaking" --color "b60205"
gh label create "high-priority" --description "High priority - major functionality issues" --color "d93f0b"
gh label create "medium-priority" --description "Medium priority - minor functionality issues" --color "fbca04"
gh label create "low-priority" --description "Low priority - cosmetic or enhancement bugs" --color "0e8a16"

REM Component Labels
gh label create "execution" --description "Graph execution and data flow issues" --color "1d76db"
gh label create "ui" --description "User interface and interaction problems" --color "5319e7"
gh label create "file-ops" --description "File operations and persistence issues" --color "f9d0c4"
gh label create "node-system" --description "Node creation, editing, and management" --color "c2e0c6"
gh label create "undo-redo" --description "Command system and state management" --color "fef2c0"
gh label create "performance" --description "Speed and memory issues" --color "e99695"

REM Status Labels
gh label create "in-progress" --description "Currently being worked on" --color "0052cc"
gh label create "needs-repro" --description "Cannot reproduce the issue" --color "d4c5f9"
gh label create "blocked" --description "Blocked by external dependency" --color "000000"

echo.
echo ✅ GitHub labels setup complete!
echo.
echo You can now use these labels when creating issues:
echo   Priority: critical, high-priority, medium-priority, low-priority
echo   Component: execution, ui, file-ops, node-system, undo-redo, performance  
echo   Status: in-progress, needs-repro, blocked
echo.
echo The bug sync automation will automatically apply appropriate labels based on bug metadata.