@echo off
cd /d "%~dp0"
python -m pip install --quiet --disable-pip-version-check playwright
python scholar_server.py
