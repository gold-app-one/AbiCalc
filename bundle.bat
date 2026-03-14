@echo off
pyinstaller --onefile --name AbiCalc --icon=logo.ico --add-data "ui/styles/themes;ui/styles/themes" main.py
pause
