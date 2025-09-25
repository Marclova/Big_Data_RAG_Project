@echo off
@REM echo creating a new temporary virtual environment, installing modules and activating it...
@REM @echo on
@REM python -m venv .venv

@REM .\.venv\Scripts\pip install pyyaml
@REM .\.venv\Scripts\pip install pymupdf
@REM .\.venv\Scripts\pip install requests

call .\.venv\Scripts\activate
@echo off

echo:
echo installation completed.
echo:
echo Now setting the local variables for folder navigation in project: Big_Data_RAG_Project...
echo:

@REM get the full path of the folder where this script is located (without this file's name)
set folderPath=%~dp0
@REM remove trailing backslash both at the start and end (I don't know why it works like this)
set folderPath=%folderPath:~0,-1%
@REM replace the first occurrence of "Big_Data_RAG_Project." with "#" as a delimiter
set folderPath=%folderPath:Big_Data_RAG_Project\=#%

@REM split the string into two parts using the "#" delimiter
for /f "tokens=1* delims=#" %%a in ("%folderPath%") do (
    set folderPath=%%b
    set rootFolder=%%aBig_Data_RAG_Project
)

@REM replace backslashes with dots
set folderPath=%folderPath:\=.%

@REM go to the root folder
cd %rootFolder%

echo:
echo Initializing files execution in folder: %folderPath%
echo:

@REM run all Python files in the current folder
for %%f in ("%~dp0*.py") do (
    echo ======================================================================
    echo Running %%~nxf:
    python -m %folderPath%.%%~nf
    echo ======================================================================
    echo:
)

@REM echo:
@REM echo removing the temporary virtual environment...
@REM rmdir /s /q "%folderPath:.=\%\.venv"

pause