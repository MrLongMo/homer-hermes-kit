#!/bin/bash
# 砌 Mac 版：中文 dist/Homer-Mover-mac-zh.zip、英文 dist/Homer-Mover-mac-en.zip
# 只砌一個：./build_mac.sh zh  或  ./build_mac.sh en
set -euo pipefail
cd "$(dirname "$0")"
cp ../dist/homer.tar.gz homer_mover/data/homer.tar.gz
PY=../.venv/bin/python
for L in ${1:-zh en}; do
  if [ "$L" = zh ]; then NAME="Homer 搬家"; else NAME="Homer Mover"; fi
  echo "$L" > homer_mover/data/lang.txt
  $PY -m PyInstaller --noconfirm --clean --windowed --name "$NAME" \
    --osx-bundle-identifier "com.homer.hermes-mover.$L" \
    --add-data "homer_mover/ui:homer_mover/ui" --add-data "homer_mover/data:homer_mover/data" \
    --distpath "dist/$L" --workpath "build/$L" run.py >/dev/null
  (cd "dist/$L" && rm -f "../Homer-Mover-mac-$L.zip" && ditto -c -k --keepParent "$NAME.app" "../Homer-Mover-mac-$L.zip")
done
echo zh > homer_mover/data/lang.txt
ls -la dist/*.zip
