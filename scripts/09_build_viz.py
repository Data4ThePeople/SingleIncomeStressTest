"""Build dist/index.html: one self-contained page (no CDN, no library).

Inlines src/core.js, the map data (data/processed/map_data.json, gzip + base64, decoded
in the browser with the native DecompressionStream) and both D4TP logos. Then parse-checks
the script with macOS jsc and loads the page in headless Chrome (full page, embed, change
view, a selected area) and stops on any JavaScript error. With --shots it also saves screenshots
to the folder given."""
import base64
import gzip
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DIST = ROOT / "src", ROOT / "dist"
JSC = Path("/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def inline_logo(path, cls):
    svg = path.read_text()
    svg = svg[svg.index("<svg"):]
    svg = svg.replace("<svg ", f'<svg class="{cls}" role="img" aria-label="Data 4 The People" ', 1)
    return svg.replace("<style>.cls-1{fill:#fff;}</style>", "").replace('class="cls-1"', 'fill="#fff"')


def main():
    html = (SRC / "template.html").read_text()
    core = (SRC / "core.js").read_text()
    data = (ROOT / "data" / "processed" / "map_data.json").read_bytes()
    b64 = base64.b64encode(gzip.compress(data, 9)).decode("ascii")
    for marker, value in [("/*__CORE__*/", core), ("/*__DATA__*/", f'const DATA_B64 = "{b64}";'),
                          ("<!--__LOGO_ON_LIGHT__-->", inline_logo(ROOT / "assets" / "d4tp-text-dark.svg", "logo logo-light")),
                          ("<!--__LOGO_ON_DARK__-->", inline_logo(ROOT / "assets" / "d4tp-text-light_3.svg", "logo logo-dark"))]:
        assert html.count(marker) == 1, f"marker {marker} must appear exactly once"
        html = html.replace(marker, value)
    assert not re.search(r"""(src|href)=["']https?://""", html), "external resource found; the page must be self-contained"
    assert "—" not in core and "—" not in (SRC / "template.html").read_text(), "em dash in page text"

    if JSC.exists():
        i = html.index("<script>") + 8
        js = html[i:html.index("</script>", i)].replace(b64, "")
        with tempfile.TemporaryDirectory() as d:
            Path(d, "page.js").write_text(js)
            Path(d, "chk.js").write_text('try{ new Function(read("%s/page.js")); print("ok") }catch(e){ print("PARSE ERROR: "+e) }' % d)
            out = subprocess.run([str(JSC), f"{d}/chk.js"], capture_output=True, text=True).stdout.strip()
        assert out == "ok", out

    DIST.mkdir(exist_ok=True)
    out_path = DIST / "index.html"
    out_path.write_text(html)
    print(f"wrote {out_path}: {out_path.stat().st_size / 1e6:.2f} MB (data {len(b64) / 1e6:.2f} MB base64)")

    if Path(CHROME).exists():
        probe = html.replace("<script>", '<script>window.onerror=(m,u,l,c)=>{document.body.setAttribute("data-err",m+" @"+l+":"+c)};'
                             'window.addEventListener("unhandledrejection",e=>document.body.setAttribute("data-err","promise: "+e.reason));', 1)
        with tempfile.TemporaryDirectory() as d:
            Path(d, "probe.html").write_text(probe)
            for mode in ("", "#embed=1", "#view=change", "#a=22380&y=2024&embed=1", "#y=2016&m=pct&p=0", "#est=0&y=2024", "#st=20", "#fam=1-2"):
                dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000", "--window-size=1200,900",
                                      "--dump-dom", f"file://{d}/probe.html{mode}"], capture_output=True, text=True, timeout=300).stdout
                err = re.search(r'data-err="([^"]*)"', dom)
                assert dom and not err, f"JavaScript error ({mode or 'full page'}): {err.group(1) if err else 'no output from Chrome'}"
                sub = re.search(r'id="sub"[^>]*>([^<]*)<', dom)
                print(f"  ok {mode or 'full page':26s} -> {sub.group(1) if sub else '?'}")
            if "--shots" in sys.argv:
                out = Path(sys.argv[sys.argv.index("--shots") + 1])
                out.mkdir(parents=True, exist_ok=True)
                for name, mode, size in [("wide", "#embed=1", "1200,780"), ("flagstaff", "#a=22380&y=2024&embed=1", "1200,780"),
                                         ("change", "#view=change&m=pct&embed=1", "1200,780"), ("fam", "#fam=1-1&a=22380&y=2024&embed=1", "1200,780"), ("y2015", "#y=2015&embed=1", "1200,780"),
                                         ("narrow", "#embed=1", "420,780"), ("full", "", "1300,900")]:
                    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=8000",
                                    f"--window-size={size}", f"--screenshot={out / (name + '.png')}", f"file://{d}/probe.html{mode}"],
                                   capture_output=True, timeout=300)
                print(f"  screenshots in {out}")


if __name__ == "__main__":
    main()
