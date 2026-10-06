"""GIF of the live map as the cushion slides from $0 to $25,000 (median earner, starting settings).

Drives dist/index.html (embed view, 1200x780) in headless Chrome, setting the slider one $500 step
at a time, so the map, the slider and the headline are the page's own. Output:
posts/stress-test-viz/images/03-cushion-slider.gif

  .venv/bin/python video/build_gif.py
"""
import json
import time

from PIL import Image

from build_video import BUILD, ROOT, Chrome

OUT = ROOT / "posts" / "stress-test-viz" / "images" / "03-cushion-slider.gif"
VW, VH, OUT_W = 1200, 780, 1000
STEP_MS, HOLD_MS = 110, 1500


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    ch = Chrome(port=9346)
    try:
        ch.cmd("Emulation.setDeviceMetricsOverride", width=VW, height=VH, deviceScaleFactor=1, mobile=False)
        ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=1&debug=1")
        for _ in range(120):
            time.sleep(0.25)
            try:
                if ch.js("!!window.__ssdbg"):
                    break
            except Exception:
                pass
        # recording only: keep the headline on one line so the page does not shift when the count grows
        ch.js("document.getElementById('sub').style.cssText = 'white-space:nowrap;font-size:12.5px'")
        time.sleep(1.0)
        frames, counts = [], []
        for v in range(0, 25001, 500):
            ch.js(f"(() => {{ const e = document.getElementById('cush'); e.value = {json.dumps(str(v))}; e.dispatchEvent(new Event('input')); }})()")
            ch.frame_done()
            counts.append((v, ch.js("document.getElementById('sub').textContent")))
            im = ch.shot()
            frames.append(im.resize((OUT_W, round(im.height * OUT_W / im.width)), Image.LANCZOS))
    finally:
        ch.close()
    pal = frames[len(frames) // 2].quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE)   # one palette for every frame
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    dur = [STEP_MS] * len(q)
    dur[0] = dur[-1] = HOLD_MS
    q[0].save(OUT, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True)
    print(f"wrote {OUT}: {len(q)} frames, {OUT.stat().st_size / 1e6:.1f} MB, {sum(dur) / 1000:.1f} s a loop")
    for v, t in (counts[0], counts[20], counts[40], counts[-1]):
        print(f"  ${v:,}: {t.split(': ', 1)[1]}")


if __name__ == "__main__":
    main()
