# 砌 Windows 版：喺 Windows 部機（或者 GitHub Actions）行
#   py -3.13 -m pip install pywebview==5.4 pyinstaller==6.11.1
#   powershell -ExecutionPolicy Bypass -File build_windows.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Copy-Item ..\dist\homer.tar.gz homer_mover\data\homer.tar.gz -Force
py -3.13 -m PyInstaller --noconfirm --clean --windowed --onefile --name "Homer-Mover-win" `
  --add-data "homer_mover/ui;homer_mover/ui" --add-data "homer_mover/data;homer_mover/data" run.py
Get-ChildItem dist
