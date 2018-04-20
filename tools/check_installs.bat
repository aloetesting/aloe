rem Check that the package installs

rem Always clean up
rem https://stackoverflow.com/a/28890881/288201
if "%~1" equ ":main" (
    shift /1
    goto main
)

cmd /d /c "%~f0" :main %*
if exist check_install_dist rmdir /s /q check_install_dist
if exist check_install_venv rmdir /s /q check_install_venv
exit /b

:main

rem Build the distribution, in a separate directory
if exist check_install_dist rmdir /s /q check_install_dist
python setup.py sdist -d check_install_dist || goto :error

rem Prepare a clean virtual environment
deactivate
if exist check_install_venv rmdir /s /q check_install_venv
virtualenv check_install_venv || goto :error
call check_install_venv\Scripts\activate.bat
rem echo is unset in activate.bat, turn it back on
@echo on

rem Install the package
for %%a in (check_install_dist\*.tar.gz) do pip install %%a || goto :error

rem Smoke test
aloe --version || goto :error

exit /b

:error
exit /b %errorlevel%
