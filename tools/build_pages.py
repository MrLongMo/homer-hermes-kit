"""砌 GitHub Pages 靜態版（冇電子報後台）：輸出到 <out>，路徑改成相對路徑。
用法：python3 tools/build_pages.py <輸出資料夾>"""
import pathlib, re, shutil, sys

site = pathlib.Path(__file__).resolve().parent.parent / "site"
out = pathlib.Path(sys.argv[1])
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
shutil.copytree(site / "assets", out / "assets")
shutil.copytree(site / "img", out / "img")

sub = (out / "assets" / "subscribe.js").read_text()
sub = sub.replace('      fetch("/api/subscribe", {', '      (function () { return Promise.reject(0); })("/api/subscribe", {')
sub = sub.replace('msg.textContent = "網路連線有問題，請稍後再試。";', 'msg.textContent = "電子報即將開放，敬請期待！先到 GitHub 下載程式吧。";')
assert "即將開放" in sub
(out / "assets" / "subscribe.js").write_text(sub)

for rel in ["index.html", "grok-bot-to-hermes/index.html", "en/index.html", "en/grok-bot-to-hermes/index.html"]:
    up = "../" * rel.count("/")
    html = (site / rel).read_text()
    html = html.replace('<link rel="canonical" href="/grok-bot-to-hermes/">\n', "")
    html = re.sub(r'(href|src)="/(?!/)([^"]*)"', lambda m: f'{m.group(1)}="{(up + m.group(2)) or "./"}"', html)
    html = html.replace('<a href="SUBSTACK_URL">English</a>', f'<a href="{up}en/">English</a>')
    assert not re.search(r'(href|src)="/(?!/)', html), rel
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
(out / ".nojekyll").write_text("")
print("ok", out)
