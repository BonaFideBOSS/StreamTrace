@echo off

REM Get the IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4 Address"') do set ip=%%a
set ip=%ip:~1%

REM Activate the virtual environment
call venv\Scripts\activate
call cd app

REM Install the requirements
python -m pip install -r requirements.txt

REM Run the Flask app
start "Techwiz4" cmd /c "python -m flask --debug run --host=0.0.0.0"

REM Open the Flask app in the default browser
timeout /t 5
start "" http://%ip%:5000