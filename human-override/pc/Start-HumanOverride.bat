@echo off
rem Human Override for Windows - (c) 2026 Amghar Said. Starts the PowerShell script as administrator.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0HumanOverride.ps1"
