"""YouTube thumbnail for the tutorial video: 1280x720 PNG -> video/single-income-stress-test-thumbnail.png.

Screenshots the live map (2025, starting settings) from dist/index.html in headless Chrome, then sets it
on the viz's light paper beside a title in the video's type and colors.

  .venv/bin/python video/thumbnail.py
"""
import base64
import io
import json
import time

from PIL import Image

import importlib.util

from build_video import BUILD, CORAL, INK, PAPER, ROOT, Chrome

TW, TH = 1280, 720
OUT = ROOT / "video" / "single-income-stress-test-thumbnail.png"


def map_shot(ch):
    ch.cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=2, mobile=False)
    ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=1&debug=1")
    for _ in range(120):
        time.sleep(0.25)
        try:
            if ch.js("!!window.__ssdbg"):
                break
        except Exception:
            pass
    ch.js("document.getElementById('ss').style.height = '900px'")
    ch.js("document.getElementById('legend').style.display = 'none'")
    time.sleep(1.5)
    r = ch.js("(() => { const r = document.getElementById('mapbox').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()")
    d = ch.cmd("Page.captureScreenshot", format="png",
               clip=dict(x=r[0], y=r[1], width=r[2], height=r[3], scale=1))["data"]
    return Image.open(io.BytesIO(base64.b64decode(d))).convert("RGB")


def logo_on_light():
    spec = importlib.util.spec_from_file_location("bv", ROOT / "scripts" / "09_build_viz.py")
    bv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bv)
    return bv.inline_logo(ROOT / "assets" / "d4tp-text-dark.svg", "logo")


def main():
    ch = Chrome(port=9345)
    try:
        m = map_shot(ch)
        m.save(BUILD / "thumb-map.png")
        html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
        html,body{{margin:0;width:{TW}px;height:{TH}px;overflow:hidden;background:{PAPER};color:{INK};
          font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
        .map{{position:absolute;right:-110px;top:50%;transform:translateY(-50%);height:800px;width:auto;mix-blend-mode:multiply}}
        .shade{{position:absolute;inset:0;background:linear-gradient(90deg,{PAPER} 0%,{PAPER} 44%,rgba(247,245,239,.85) 53%,rgba(247,245,239,0) 66%)}}
        .txt{{position:absolute;left:64px;top:0;bottom:0;width:760px;display:flex;flex-direction:column;justify-content:center}}
        .logo{{height:44px;width:auto;display:block;margin-bottom:40px;align-self:flex-start}}
        .kicker{{display:inline-block;align-self:flex-start;background:{CORAL};color:#fff;font-weight:800;font-size:30px;
          letter-spacing:.12em;text-transform:uppercase;padding:8px 18px 6px;border-radius:8px;margin-bottom:26px}}
        h1{{font-size:104px;line-height:.98;margin:0;font-weight:800;letter-spacing:-.01em}}
        .sub{{font-size:30px;color:#5F6B67;margin-top:26px;font-weight:600}}
        </style></head><body>
        <img class="map" src="file://{BUILD / 'thumb-map.png'}">
        <div class="shade"></div>
        <div class="txt">{logo_on_light()}<div class="kicker">How to use</div>
          <h1>The Single<br>Income<br>Stress Test</h1>
          <div class="sub">Every U.S. metro and rural area, 2015 to 2025</div></div>
        </body></html>"""
        p = BUILD / "thumbnail.html"
        p.write_text(html)
        ch.cmd("Emulation.setDeviceMetricsOverride", width=TW, height=TH, deviceScaleFactor=1, mobile=False)
        ch.cmd("Page.navigate", url=f"file://{p}")
        time.sleep(1.5)
        ch.shot().save(OUT, optimize=True)
        print("wrote", OUT)
    finally:
        ch.close()


if __name__ == "__main__":
    main()
