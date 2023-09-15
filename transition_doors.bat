set INI_FILE="C:\Users\steve\Desktop\DOORS\transition_door\config.ini"
set APP_DIR= "C:\Users\steve\Desktop\DOORS\transition_door"

SET original_path=%~dp0
call activate sas_door
call cd /D %APP_DIR%
:: set PYTHON_MAIN_APP= %APP_DIR%\start_device_application.py
set PYTHON_MAIN_APP= %APP_DIR%\start_single_gate_device.py

::start pythonw %PYTHON_MAIN_APP% %INI_FILE%

:: below to debug and have output in shell
 python %PYTHON_MAIN_APP% %INI_FILE%
 call cd /D %original_path%