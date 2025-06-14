@echo off
setlocal
set ENV_NAME=venv_drone

:: A modifier par ton python et ton main
set PYTHON_EXE=C:\Users\josep\AppData\Local\Programs\Python\Python311\python.exe
set MAIN_FILE=gesture_control\main.py
set REQ_FILE=requirements.txt

:: 1. Créer le venv s'il n'existe pas
if not exist "%ENV_NAME%" (
    echo [INFO] Creating virtual environment %ENV_NAME%...
    "%PYTHON_EXE%" -m venv "%ENV_NAME%"
)

:: 2. Activer l’environnement
call "%ENV_NAME%\Scripts\activate"

:: 3. Installer les packages depuis requirements.txt
if exist "%REQ_FILE%" (
    echo [INFO] Installing packages from %REQ_FILE%...
    pip install --upgrade pip
    pip install -r "%REQ_FILE%"
) else (
    echo [WARNING] No requirements.txt found. Skipping package installation.
)

:: 4. Lancer le script
echo [INFO] Running %MAIN_FILE%...
python "%MAIN_FILE%"

endlocal
pause