@echo off
"git" "stash"
"git" "stash" "clear"
"git" "pull" "origin" "master"
"pip" "install" "-r" "requirements.txt"
