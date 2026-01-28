::to run this batch file you need to write its name+extension in a terminal.
:: From the root folder of the project, you can run: .\tests\covering_tests\.portable_autoRunner.bat

@echo off
::#region get folder path and root folder of the project named 'Big_Data_RAG_Project'

::get the relative path of the folder where this script is located (without this file's name)
set folderPath=%~dp0
::replace the first occurrence of "Big_Data_RAG_Project." with "#" as a delimiter
set folderPath=%folderPath:Big_Data_RAG_Project\=#%

::split the string into two parts using the "#" delimiter
for /f "tokens=1* delims=#" %%a in ("%folderPath%") do (
    set folderPath=%%b
    set rootFolder=%%aBig_Data_RAG_Project
)
@REM set folderPath=%rootFolder%\%folderPath%
set folderPath=%folderPath%


::go to the root folder (if not already there)
cd %rootFolder%

::#endregion get folder path and root folder of the project named 'Big_Data_RAG_Project'

echo:
echo detected project root folder: %rootFolder%
echo detected target folder for tests execution: %folderPath%
echo:


echo Now creating a new temporary virtual environment, installing modules and activating it...
@echo on
python -m venv %folderPath%.venv

::install required modules
%folderPath%.venv\Scripts\pip install pyyaml
%folderPath%.venv\Scripts\pip install pymupdf
%folderPath%.venv\Scripts\pip install requests
%folderPath%.venv\Scripts\pip install pymongo
%folderPath%.venv\Scripts\pip install fitz
%folderPath%.venv\Scripts\pip install frontend

call %folderPath%.venv\Scripts\activate
@echo off

echo:
echo Initializing files execution in folder: %folderPath%
echo:

::substitute backslashes with dots for module path usage
set folderPath=%folderPath:\=.%

::run all Python files in the current folder
for %%f in ("%~dp0*.py") do (
    echo ======================================================================
    echo Running %%~nxf:
    python -m %folderPath%%%~nf
    echo ======================================================================
    echo:
)

::cleanup temporary virtual environment
@REM echo:
@REM echo removing the temporary virtual environment...
@REM rmdir /s /q "%folderPath:.=\%\.venv"

pause