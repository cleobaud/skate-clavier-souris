@echo off
chcp 65001 >nul
title skate. au clavier et a la souris
cd /d "%~dp0"

echo.
echo   ==========================================================
echo     skate. - clavier et souris
echo   ==========================================================
echo.

rem --- 1. Python ---
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py -3"
if not defined PY goto SANS_PYTHON

rem --- 2. la bibliotheque vgamepad (une seule fois) ---
%PY% -c "import vgamepad" >nul 2>nul
if errorlevel 1 (
  echo   Installation de la bibliotheque vgamepad, une seule fois...
  %PY% -m pip install --user -r requirements.txt
  echo.
)

rem --- 3. la manette virtuelle (pilote ViGEmBus) ---
echo   Verification de la manette virtuelle...
echo.
%PY% verifier_manette.py
if errorlevel 1 goto SANS_PILOTE

rem --- 4. on joue ---
echo.
%PY% skate_kbm.py
goto FIN

:SANS_PYTHON
echo   Python n'est pas installe.
echo   1. Installe Python 3 depuis python.org (coche "Add python.exe to PATH").
echo   2. Relance JOUER.bat.
echo.
start "" "https://www.python.org/downloads/"
pause
goto FIN

:SANS_PILOTE
echo.
echo   Le pilote de manette virtuelle ViGEmBus manque ou n'est pas actif.
echo   1. Sur la page qui s'ouvre (depot officiel de Nefarius), telecharge
echo      ViGEmBus_1.22.0_x64_x86_arm64.exe et installe-le.
echo   2. Redemarre le PC.
echo   3. Relance JOUER.bat.
echo.
start "" "https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0"
pause
goto FIN

:FIN
