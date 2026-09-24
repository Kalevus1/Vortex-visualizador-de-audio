@echo off
REM Genera el ejecutable en DOS formatos: CARPETA (dist\Visualizador\) y EMPAQUETADO (dist\Visualizador.exe).
cd /d "%~dp0"
set "PYDIR=..\.venv_face\Scripts"
if not exist "%PYDIR%\python.exe" set "PYDIR=.venv\Scripts"
if not exist "%PYDIR%\pyinstaller.exe" ( echo Instalando PyInstaller... & "%PYDIR%\python.exe" -m pip install pyinstaller )

set OPTS=--collect-all pyqtgraph --collect-all OpenGL --collect-all sounddevice --collect-all soundfile
set EXCL=--exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets --exclude-module PySide6.QtQml --exclude-module PySide6.Qt3DCore --exclude-module PySide6.QtMultimedia --exclude-module PySide6.QtPdf --exclude-module PySide6.QtWebChannel --exclude-module PySide6.QtDesigner --exclude-module scipy --exclude-module jax --exclude-module jaxlib --exclude-module matplotlib --exclude-module cv2 --exclude-module mediapipe --exclude-module tensorflow --exclude-module torch

echo === 1/2  CARPETA (onedir) ===
"%PYDIR%\pyinstaller.exe" --noconfirm --clean --windowed --onedir ^
  --name "Visualizador" --icon "recursos\icono.ico" %OPTS% %EXCL% visualizador_audio.py

echo === 2/2  EMPAQUETADO (onefile) ===
"%PYDIR%\pyinstaller.exe" --noconfirm --windowed --onefile ^
  --name "Visualizador" --icon "recursos\icono.ico" %OPTS% %EXCL% visualizador_audio.py
echo.
echo Listo:  dist\Visualizador\Visualizador.exe   y   dist\Visualizador.exe
pause
