@echo off
color 03
title Gladiatorerna - Console

py frontend.py

if %errorlevel% neq 0 (
    echo.
    echo An error has occured. Press any key to close this console.
    echo.
)
exit /b %errorlevel%