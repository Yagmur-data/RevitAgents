@echo off
rem Double-click to install the Revit 2025 add-in + MCP server for the Claude Code agents.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-claude-code.ps1" %*
pause
