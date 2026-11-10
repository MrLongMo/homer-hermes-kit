"""假 hermes：扮官方 CLI 嘅回應，俾測試用。狀態寫喺 $HERMES_HOME/_fake.json。"""
import json
import os
import sys
import tarfile
from pathlib import Path

home = Path(os.environ["HERMES_HOME"])
home.mkdir(parents=True, exist_ok=True)
state_f = home / "_fake.json"
st = json.loads(state_f.read_text()) if state_f.exists() else {"plugins": [], "login": False, "calls": []}
args = sys.argv[1:]
st["calls"].append(args)
profile = None
if args[:1] == ["-p"]:
    profile, args = args[1], args[2:]
pdir = home / "profiles" / (profile or "homer")


def save():
    state_f.write_text(json.dumps(st))


def out(s):
    print(s)


code = 0
if args == ["--version"]:
    out(f"Hermes Agent v{os.environ.get('FAKE_VERSION', '0.22.7')} (fake)")
elif args[:2] == ["profile", "import"]:
    with tarfile.open(args[2]) as t:
        t.extractall(home / "profiles", filter="data")
    out("Imported profile 'homer'")
elif args[:2] == ["profile", "use"]:
    out(f"Default profile set to {args[2]}")
elif args[:2] == ["auth", "status"]:
    out("xai-oauth: logged in" if st["login"] else "xai-oauth: not logged in")
elif args[:2] == ["auth", "add"]:
    out("Open this URL to sign in: https://accounts.x.ai/device?user_code=ABCD-1234")
    out("Enter code: ABCD-1234")
    out("Waiting for approval...")
    st["login"] = True
    out("Login successful")
elif args[:2] == ["plugins", "list"]:
    out("\n".join(st["plugins"]) or "No plugins installed")
elif args[:2] == ["plugins", "install"]:
    st["plugins"].append(args[2])
    out(f"Installed {args[2]}")
elif args[:2] == ["import-agent", "grok-bot"]:
    rest = args[2:]
    if "--source" not in rest:
        d = pdir / "grok-bot-import"
        d.mkdir(parents=True, exist_ok=True)
        prompt = "Please export your setup for Hermes. " * 12
        (d / "export-prompt.txt").write_text(prompt)
        out("No Grok Bot export found. Paste this into your Bot:\n\n" + prompt)
    else:
        src = Path(rest[rest.index("--source") + 1])
        if not src.is_file():
            out(f"error: {src} not found")
            code = 2
        elif "--dry-run" in rest:
            out("Plan for bot 'Trip Planner':\n  • soul: role → SOUL.md\n  • 3 skills → skills/grok-bot-imports\n"
                "  • 4 memories → MEMORY.md\n  • 1 routine → paused cron job\nDry run: nothing written.")
        elif "-y" in rest:
            (pdir / "memories").mkdir(parents=True, exist_ok=True)
            out("Imported: 3 skills, 4 memories, 1 routine (paused)")
        else:
            out("Preview only (no -y).")
elif args[:2] == ["config", "set"]:
    st.setdefault("config", {})[args[2]] = args[3]
    out(f"Set {args[2]} = {args[3]}")
elif args == ["update"]:
    out("Updated")
else:
    out("unknown: " + " ".join(args))
    code = 1
save()
sys.exit(code)
