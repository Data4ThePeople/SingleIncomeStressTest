"""Tutorial video for the Single Income Stress Test: 1920x1080, 30 fps, about 57 s.

Same format as the child poverty tutorial (../ChildPovertyDistrict/video/build_video.py). Drives the
built viz (dist/index.html, embed view, light theme) in headless Chrome through the DevTools
protocol: real mouse moves, clicks and typing, so tooltips and outlines behave as they do for
readers. Each frame is composited with a drawn cursor, click ripples and a caption, between an intro
card and a logo card that fades to black. Numbers in captions are read from the page itself.

  .venv/bin/python video/music.py                  # render the music first -> video/build/music.wav
  .venv/bin/python video/build_video.py            # full render -> video/single-income-stress-test-tutorial.mp4
  .venv/bin/python video/build_video.py --sheet    # stills only -> video/build/contact-sheet.png
"""
import base64
import importlib.util
import io
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import imageio_ffmpeg
import websocket
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "video" / "build"
OUT = ROOT / "video" / "single-income-stress-test-tutorial.mp4"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FPS, W, H = 30, 1920, 1080
VW, VH, DSF = 1600, 900, 1.2            # viz viewport (CSS px) and scale -> the full 1920 x 1080 frame
INK, PAPER, CORAL, GREEN, DARK, MUTED = "#1F2A27", "#F7F5EF", "#f37952", "#085041", "#181A1B", "#8C9094"
SANS = "/System/Library/Fonts/SFNS.ttf"
T_TOUR, T_OUT, T_FADE, T_END = 4.0, 51.0, 55.5, 57.0      # tour starts, logo card, fade to black, end
CITY, CITY_ID = "Cincinnati", "17140"
STATE, STATE_NAME = "12", "Florida"


# ---------- Chrome over the DevTools protocol ----------
class Chrome:
    def __init__(self, port=9344):
        self.proc = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={port}",
                                      f"--remote-allow-origins=http://127.0.0.1:{port}", "--hide-scrollbars",
                                      f"--user-data-dir={BUILD / ('chrome-' + str(port))}", "about:blank"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                break
            except Exception:
                time.sleep(0.25)
        page = [t for t in tabs if t["type"] == "page"][0]
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=120)
        self.i = 0

    def cmd(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.i:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})

    def js(self, expr):
        r = self.cmd("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r:
            raise RuntimeError(f"JS error: {r['exceptionDetails']}\n{expr[:200]}")
        return r["result"].get("value")

    def frame_done(self):
        self.js("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")

    def shot(self):
        d = self.cmd("Page.captureScreenshot", format="png")["data"]
        return Image.open(io.BytesIO(base64.b64decode(d))).convert("RGB")

    def mouse(self, kind, x, y):
        self.cmd("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left" if kind != "mouseMoved" else "none",
                 clickCount=1 if kind != "mouseMoved" else 0)

    def close(self):
        self.proc.terminate()


# ---------- cards (HTML rendered by Chrome so the type matches the viz) ----------
def logo_svg(cls_light=True):
    spec = importlib.util.spec_from_file_location("bv", ROOT / "scripts" / "09_build_viz.py")
    bv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bv)
    return bv.inline_logo(ROOT / "assets" / "d4tp-text-light_3.svg", "logo")   # logo for dark backgrounds


def card_html(body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
    html,body{{margin:0;width:{W}px;height:{H}px;background:{DARK};color:#E4E2DC;
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
    .wrap{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
    .logo{{height:76px;width:auto;display:block;margin-bottom:56px}}
    .kicker{{font-size:34px;letter-spacing:.14em;text-transform:uppercase;color:{CORAL};font-weight:600;margin-bottom:22px}}
    h1{{font-size:84px;line-height:1.05;margin:0;font-weight:700;max-width:1500px}}
    .sub{{font-size:34px;color:#BBBDC0;margin-top:30px}}
    .rule{{width:120px;height:6px;background:{CORAL};border-radius:3px;margin:40px auto 0}}
    .big .logo{{height:120px;margin-bottom:46px}}
    .url{{font-size:46px;font-weight:600;color:#E4E2DC}}
    .small{{font-size:28px;color:{MUTED};margin-top:18px}}
    </style></head><body>{body}</body></html>"""


def render_cards(ch):
    logo = logo_svg()
    intro = card_html(f"""<div class="wrap">{logo}<div class="kicker">Tutorial</div>
      <h1>How to use the<br>Single Income Stress Test</h1>
      <div class="sub">Every U.S. metro and rural area, 2015 to 2025</div><div class="rule"></div></div>""")
    outro = card_html(f"""<div class="wrap big">{logo}<div class="url">Free at data4thepeople.com</div>
      <div class="small">The Single Income Stress Test, 2015 to 2025</div></div>""")
    cards = {}
    ch.cmd("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1, mobile=False)
    for name, html in (("intro", intro), ("outro", outro)):
        p = BUILD / f"{name}.html"
        p.write_text(html)
        ch.cmd("Page.navigate", url=f"file://{p}")
        time.sleep(1.0)
        cards[name] = ch.shot()
        cards[name].save(BUILD / f"card-{name}.png")
    return cards


# ---------- drawing helpers ----------
def font(size, bold=False):
    f = ImageFont.truetype(SANS, size)
    try:
        f.set_variation_by_name("Bold" if bold else "Regular")
    except Exception:
        pass
    return f


CURSOR = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]


def draw_cursor(img, x, y, ripples, t):
    d = ImageDraw.Draw(img, "RGBA")
    for (rt, rx, ry) in ripples:
        a = (t - rt) / 0.45
        if 0 <= a <= 1:
            r = 10 + 46 * a
            d.ellipse([rx - r, ry - r, rx + r, ry + r], outline=(243, 121, 82, int(230 * (1 - a))), width=5)
    s = 1.25
    pts = [(x + px * s, y + py * s) for px, py in CURSOR]
    shadow = [(px + 3, py + 4) for px, py in pts]
    d.polygon(shadow, fill=(0, 0, 0, 70))
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(20, 20, 20, 255))
    d.line(pts + [pts[0]], fill=(20, 20, 20, 255), width=2)


def wrap(text, f, maxw, d):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=f) > maxw and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = trial
    return lines + [cur]


def draw_caption(img, text, t, t0, t1, anchor, step, nsteps):
    """IG-style caption: types in near the action on a dark rounded box, fades out at the end."""
    f, fs = font(46, bold=True), font(24, bold=True)
    d = ImageDraw.Draw(img, "RGBA")
    lines = wrap(text, f, 780, d)              # wrap the full text so lines never reflow while typing
    shown = int(max(0, t - t0 - 0.15) * 25)    # 25 characters a second
    alpha = min(1.0, (t - t0) / 0.2, max(0.0, (t1 - t) / 0.35))
    if alpha <= 0:
        return
    typed, left = [], shown
    for ln in lines:
        typed.append(ln[:max(0, left)])
        left -= len(ln) + 1
    typing = shown < len(text)
    lh, px, py = 58, 30, 22
    boxw = max(d.textlength(ln, font=f) for ln in lines) + 2 * px
    boxh = 34 + len(lines) * lh + 2 * py - 8
    x, y, align = anchor
    if align == "right":
        x -= boxw
    x, y = max(28, min(W - boxw - 28, x)), max(28, min(H - boxh - 28, y))
    a = int(225 * alpha)
    d.rounded_rectangle([x + 4, y + 6, x + boxw + 4, y + boxh + 6], 20, fill=(0, 0, 0, int(60 * alpha)))
    d.rounded_rectangle([x, y, x + boxw, y + boxh], 20, fill=(24, 26, 27, a))
    d.text((x + px, y + py - 4), f"{step} / {nsteps}", font=fs, fill=(243, 121, 82, int(255 * alpha)))
    for k, ln in enumerate(typed):
        d.text((x + px, y + py + 30 + k * lh), ln, font=f, fill=(247, 245, 239, int(255 * alpha)))
    if typing and int(t * 3) % 2 == 0:          # caret while typing
        k = max(0, min(len(typed) - 1, next((i for i, ln in enumerate(typed) if len(ln) < len(lines[i])), len(typed) - 1)))
        cx = x + px + d.textlength(typed[k], font=f) + 4
        cy = y + py + 30 + k * lh
        d.rectangle([cx, cy + 6, cx + 4, cy + 50], fill=(243, 121, 82, int(255 * alpha)))


def ease(a):
    a = min(1, max(0, a))
    return a * a * (3 - 2 * a)


# ---------- the tour ----------
def main():
    sheet = "--sheet" in sys.argv
    BUILD.mkdir(parents=True, exist_ok=True)
    ch = Chrome()
    cards = render_cards(ch)
    ch.cmd("Emulation.setDeviceMetricsOverride", width=VW, height=VH, deviceScaleFactor=DSF, mobile=False)
    ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=1&debug=1")
    for _ in range(120):
        time.sleep(0.25)
        try:
            if ch.js("!!window.__ssdbg"):
                break
        except Exception:
            pass
    ch.js("document.getElementById('ss').style.height = '900px'")   # recording only: let the map fill the frame
    time.sleep(1.0)
    rect = lambda sel: ch.js(f"(() => {{ const r = document.querySelector({json.dumps(sel)}).getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }})()")
    fire = lambda el, value, ev: ch.js(f"(() => {{ const e = document.getElementById({json.dumps(el)}); e.value = {json.dumps(str(value))}; e.dispatchEvent(new Event({json.dumps(ev)})); }})()")
    set_year = lambda i: fire("year", i, "input")
    thumb = lambda v: ch.js(f"(() => {{ const r = document.getElementById('cush').getBoundingClientRect(); return [r.x + 8 + ({v} / 25000) * (r.width - 16), r.y + r.height / 2]; }})()")

    # numbers for the captions: set the page, read its own headline, put it back
    def headline(setup, undo):
        ch.js(f"(() => {{ const S = __ssdbg.S; {setup}; __ssdbg.update(); }})()")
        text = ch.js("document.getElementById('sub').textContent")
        ch.js(f"(() => {{ const S = __ssdbg.S; {undo}; __ssdbg.update(); }})()")
        m = re.search(r"falls short in ([\d,]+) of ([\d,]+) areas", text)
        return m.group(1), m.group(2)

    c0, total = headline("S.cush = 0", "S.cush = 10000")
    c20, _ = headline("S.cush = 20000", "S.cush = 10000")
    p25, _ = headline("S.p = 1", "S.p = 2")
    p75, _ = headline("S.p = 3", "S.p = 2")
    fl, fl_n = headline(f"S.st = '{STATE}'", "S.st = ''")
    assert p25 == total and p75 == "0", (p25, p75, total)
    spare = ch.js(f"(() => {{ const c = __ssdbg.calc(__ssdbg.byId.get('{CITY_ID}'), __ssdbg.S.yi); return c.dol; }})()")
    city_line = f"${spare:,} to spare" if spare >= 0 else f"short by ${-spare:,}"
    print("caption numbers:", c0, c20, total, p25, p75, fl, fl_n, city_line)

    # captions sit over open water so they never cover the country: under the lower 48 while the whole
    # map shows, and in the lower left once the map is zoomed to a city or a state
    GULF = lambda: (650, 672, "left")
    LOWLEFT = lambda: (48, 672, "left")
    steps = [
        (4.0, 14.0, f"Slide the cushion. At $0, one income falls short in {c0} of {total} areas. At $20,000, in {c20}.", GULF),
        (14.0, 21.0, "Press Play to watch 2015 to 2025", GULF),
        (21.0, 27.0, "Pick the earner. At the 25th percentile, every area falls short. At the 75th, none do.", GULF),
        (27.0, 34.0, f"Search any city to see the math: {CITY}, {city_line}", LOWLEFT),
        (34.0, 40.0, "Change the family", LOWLEFT),
        (40.0, 45.0, f"Pick a state: in {STATE_NAME}, one income falls short in {fl} of {fl_n} areas", LOWLEFT),
        (45.0, 51.0, "Reset, then click a ranking to jump there", "ranking"),
    ]

    # cursor keyframes are resolved when their segment starts (targets can move as the page changes)
    pos = [VW * 0.62, 30.0]       # start in the header, off the map, so nothing is hovered before the tour begins
    moves = []          # (t0, t1, target_fn)
    events = []         # (t, fn)
    drags = []          # (t0, t1, v0, v1): the cushion slider, value by value, with the cursor on its thumb
    ripples = []
    quiet = []          # (t0, t1): the cursor is drawn but mouse moves are not sent to the page

    def move(t0, t1, target):
        moves.append([t0, t1, target, None, None])

    def click(t, real=True):
        def fn():
            x, y = pos
            if real:
                ch.mouse("mousePressed", x, y)
                ch.mouse("mouseReleased", x, y)
            ripples.append((t, x * DSF, y * DSF))
        events.append((t, fn))

    def at(t, fn):
        events.append((t, fn))

    def choose(t, el, value):          # a dropdown: ripple on the box, then the value changes (native menus do not render headless)
        click(t, real=False)
        at(t + 0.2, lambda: fire(el, value, "change"))

    # beat 1: the cushion slider, down to $0, up to $25,000, back to $10,000
    move(4.2, 4.9, lambda: thumb(10000))
    click(5.0, real=False)
    drags.extend([(5.1, 7.0, 10000, 0), (7.6, 10.6, 0, 25000), (11.2, 12.8, 25000, 10000)])
    move(13.0, 13.9, lambda: [VW * 0.36, VH * 0.10])
    # beat 2: speed 3x, play through the years (timed by the script, not the page clock)
    move(14.1, 14.6, lambda: rect("#speed"))
    click(14.7)
    click(14.95)
    move(15.05, 15.45, lambda: rect("#play"))
    click(15.5, real=False)
    at(15.52, lambda: ch.js("document.getElementById('play').textContent = 'Pause'"))
    for k in range(11):
        at(15.6 + k * 0.42, (lambda i: (lambda: set_year(i)))(k))
    at(20.2, lambda: ch.js("document.getElementById('play').textContent = 'Play'"))
    # beat 3: the earner's place on the pay scale
    move(21.1, 21.7, lambda: rect("#pct"))
    choose(21.8, "pct", 1)
    choose(23.6, "pct", 3)
    choose(25.4, "pct", 2)
    # beat 4: search a city
    move(27.1, 27.7, lambda: rect("#q"))
    click(27.8)
    for k, c in enumerate(CITY):
        at(28.0 + k * 0.11, (lambda c: (lambda: ch.cmd("Input.insertText", text=c)))(c))
    move(29.3, 29.9, lambda: ch.js(f"""(() => {{ const li = [...document.querySelectorAll('#lb li')].find(l => l.textContent.includes({json.dumps(CITY)}));
        const r = li.getBoundingClientRect(); return [r.x + 60, r.y + r.height / 2]; }})()"""))
    click(30.0)
    # the map zooms under the cursor on that click; the page is not told about the cursor again until it
    # reaches the Area panel, so no other area gets hovered on the way and the panel keeps showing the city
    quiet.append((30.0, 30.85))
    move(30.1, 30.8, lambda: rect("#detail .spark"))
    # beat 5: the family
    move(34.1, 34.7, lambda: rect("#fam"))
    choose(34.8, "fam", "1-2")
    choose(36.6, "fam", "2-3")
    choose(38.4, "fam", "2-2")
    # beat 6: one state
    move(40.1, 40.7, lambda: rect("#state"))
    choose(40.8, "state", STATE)
    at(40.9, lambda: ch.js("document.getElementById('q').value = ''"))
    move(41.8, 42.6, lambda: rect("#rank .scope"))
    # beat 7: reset, then the first ranking
    move(45.0, 45.6, lambda: rect("#reset"))
    click(45.7)
    move(46.3, 47.1, lambda: rect("#rank tr[data-id]"))
    click(47.3)
    move(48.3, 49.2, lambda: rect("#detail .name"))
    events.sort(key=lambda e: e[0])
    anchors = {}

    def anchor_for(i, spec):
        if i not in anchors:
            if spec == "ranking":        # beside the rankings panel, level with the first row
                rx, ry = rect("#rank tr[data-id]")
                left = ch.js("document.getElementById('rank').getBoundingClientRect().x")
                anchors[i] = (left * DSF - 30, ry * DSF - 70, "right")
            else:
                anchors[i] = spec()
        return anchors[i]

    stills = {t: None for t in (5.0, 7.3, 10.9, 13.5, 17.0, 20.5, 23.0, 24.8, 29.2, 32.5, 36.0, 38.0, 43.0, 46.0, 49.5, 53.0)}
    ff = None
    if not sheet:
        ff = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-i", str(BUILD / "music.wav"), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                               "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)

    nframes = int(T_END * FPS)
    ei = 0
    last_viz = None
    last_cush = None
    t_start = time.time()
    for f in range(nframes):
        t = f / FPS
        frame = None
        if sheet and not any(abs(t - st) < 0.5 / FPS for st in stills) and not (T_TOUR - 0.4 <= t < T_OUT):
            continue                               # stills only: cards are skipped except at their still
        if t < 3.6:                                  # intro card: fade up from black, slow push-in
            k = 1.04 - 0.04 * ease(t / 3.6)
            c = cards["intro"].resize((int(W * k), int(H * k)))
            c = c.crop(((c.width - W) // 2, (c.height - H) // 2, (c.width - W) // 2 + W, (c.height - H) // 2 + H))
            frame = Image.blend(Image.new("RGB", (W, H), "black"), c, ease(t / 0.9))
        elif t < T_OUT + 0.8:
            while ei < len(events) and events[ei][0] <= t:
                events[ei][1]()
                ei += 1
            for m in moves:                        # cursor position
                t0, t1, target = m[0], m[1], m[2]
                if t0 <= t <= t1 or (t > t1 and m[4] is None and t0 <= t):
                    if m[3] is None:
                        m[3] = list(pos)
                        m[4] = target()
                    a = ease((t - t0) / (t1 - t0))
                    pos[0] = m[3][0] + (m[4][0] - m[3][0]) * a
                    pos[1] = m[3][1] + (m[4][1] - m[3][1]) * a
            for (d0, d1, v0, v1) in drags:         # slider drag: the page gets each $500 step, the cursor rides the thumb
                if d0 <= t <= d1 + 1.0 / FPS:
                    v = v0 + (v1 - v0) * ease((t - d0) / (d1 - d0))
                    step = int(round(v / 500.0)) * 500
                    if step != last_cush:
                        fire("cush", step, "input")
                        last_cush = step
                    pos[0], pos[1] = thumb(v)
            if t < T_OUT:
                need = (not sheet) or any(abs(t - st) < 0.5 / FPS for st in stills)
                if not any(q0 <= t <= q1 for q0, q1 in quiet):
                    ch.mouse("mouseMoved", pos[0], pos[1])
                if need:
                    ch.frame_done()
                    viz = ch.shot()
                    last_viz = viz
                else:
                    viz = None
            else:
                viz = last_viz
            if viz is None:
                continue
            frame = viz.copy()
            draw_cursor(frame, pos[0] * DSF, pos[1] * DSF, ripples, t)
            for k_, (s0, s1, text, spec) in enumerate(steps):
                if s0 <= t < s1:
                    draw_caption(frame, text, t, s0, s1, anchor_for(k_, spec), k_ + 1, len(steps))
            if t < T_TOUR:                         # crossfade from the intro card
                frame = Image.blend(cards["intro"], frame, ease((t - 3.6) / 0.4))
            if t >= T_OUT:                         # crossfade to the logo card
                frame = Image.blend(frame, cards["outro"], ease((t - T_OUT) / 0.8))
        elif t < T_FADE:
            frame = cards["outro"]
        else:                                      # minimal ending: fade to black
            frame = Image.blend(cards["outro"], Image.new("RGB", (W, H), "black"), ease((t - T_FADE) / (T_END - T_FADE - 0.1)))
        for st in stills:
            if stills[st] is None and abs(t - st) < 0.5 / FPS:
                stills[st] = frame.copy()
        if ff:
            ff.stdin.write(frame.tobytes())
        if f % 150 == 0:
            print(f"  t={t:5.1f}s  frame {f}/{nframes}  {time.time() - t_start:5.0f}s elapsed", flush=True)
    ch.close()
    if ff:
        ff.stdin.close()
        ff.wait()
        print("wrote", OUT)
    th = [im.resize((640, 360)) for im in stills.values() if im is not None]
    sheet_im = Image.new("RGB", (640 * 4, 360 * ((len(th) + 3) // 4)), "black")
    for i, im in enumerate(th):
        sheet_im.paste(im, ((i % 4) * 640, (i // 4) * 360))
    sheet_im.save(BUILD / "contact-sheet.png")
    for st, im in stills.items():
        if im is not None:
            im.save(BUILD / f"still-{st:04.1f}.png")
    print("wrote", BUILD / "contact-sheet.png")


if __name__ == "__main__":
    main()
