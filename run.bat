@echo off
"git" "stash"
"git" "stash" "clear"
"git" "pull" "origin" "master"
"python" "start.py"
pause