#!/usr/bin/env python3
"""砌 Homer 出品嘅 Hermes 匯入檔（dist/homer.tar.gz）。

格式跟 Hermes 官方 `hermes profile export`：
  - 一個頂層資料夾（profile 名），入面係 profile 檔案
  - 根目錄加 desktop.json，Desktop 匯入時會套用主題同側欄顏色
用法：python3 tools/build.py
"""
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE_DIR = ROOT / "profile" / "homer"
DIST = ROOT / "dist"
PROFILE_NAME = "homer"
SKIP = {".gitignore", ".DS_Store", "README.md", "LICENSE"}
# 唔准入包嘅嘢（同 Hermes 自己嘅排除清單一致嘅重點部分）
FORBIDDEN = {".env", "auth.json", "memories", "sessions", "state.db", "logs"}


def overlay() -> str:
    theme = json.loads((ROOT / "tools" / "homer-theme.json").read_text(encoding="utf-8"))
    return json.dumps({
        "version": 1,
        "skin": theme["name"],
        "mode": "dark",
        "themes": {theme["name"]: theme},
        "profileColor": theme["colors"]["primary"],
    }, ensure_ascii=False, indent=2)


def files():
    for p in sorted(PROFILE_DIR.rglob("*")):
        rel = p.relative_to(PROFILE_DIR)
        if p.is_dir() or rel.name in SKIP:
            continue
        if rel.parts[0] in FORBIDDEN:
            raise SystemExit(f"拒絕打包私人檔案：{rel}")
        yield p, rel


def add_text(tar: tarfile.TarFile, arcname: str, text: str) -> None:
    import io
    data = text.encode("utf-8")
    info = tarfile.TarInfo(arcname)
    info.size = len(data)
    info.mode = 0o644
    tar.addfile(info, io.BytesIO(data))


def main() -> None:
    DIST.mkdir(exist_ok=True)
    out = DIST / f"{PROFILE_NAME}.tar.gz"
    with tarfile.open(out, "w:gz") as tar:
        dir_info = tarfile.TarInfo(PROFILE_NAME)
        dir_info.type = tarfile.DIRTYPE
        dir_info.mode = 0o755
        tar.addfile(dir_info)
        for path, rel in files():
            tar.add(path, arcname=f"{PROFILE_NAME}/{rel.as_posix()}", recursive=False)
        add_text(tar, f"{PROFILE_NAME}/desktop.json", overlay())
    print(f"OK: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
