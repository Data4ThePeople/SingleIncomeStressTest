"""LinkedIn carousel for the takeaways post: eight 1080x1350 slides and one PDF, built from the post's
intro images and charts. The words are condensed from Eric's intro; the two figures quoted are in the post.
Output: posts/five-takeaways-single-income/social/"""
import json

from PIL import Image, ImageDraw, ImageFont

from common import PROC, ROOT

POST = ROOT / "posts" / "five-takeaways-single-income"
IMG, OUT = POST / "images", POST / "social"
W, H, M = 1080, 1350, 72
BG, INK, MUTED, CORAL = "#181A1B", "#E4E2DC", "#8C9094", "#e0604c"
SANS = "/System/Library/Fonts/SFNS.ttf"


def font(size, bold=False):
    f = ImageFont.truetype(SANS, size)
    try:
        f.set_variation_by_name("Bold" if bold else "Regular")
    except Exception:
        pass
    return f


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) > maxw and cur:
                lines.append(cur)
                cur = w
            else:
                cur = t
        lines.append(cur)
    return lines


def text(d, xy, s, size, bold=False, fill=INK, maxw=W - 2 * M, gap=1.25):
    f = font(size, bold)
    x, y = xy
    for ln in wrap(d, s, f, maxw):
        d.text((x, y), ln, font=f, fill=fill)
        y += int(size * gap)
    return y


def fit(name, w):
    im = Image.open(IMG / name).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def base(i, n):
    s = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(s)
    d.text((M, H - 70), "Data 4 The People", font=font(26, True), fill=MUTED)
    d.text((W - M, H - 70), f"{i} / {n}", font=font(26), fill=MUTED, anchor="ra")
    return s, d


def main():
    N = json.loads((PROC / "takeaways.json").read_text())
    r0, r1 = N["t4"]["ratio_2015"], N["t4"]["ratio_2025"]
    OUT.mkdir(parents=True, exist_ok=True)
    n, slides = 8, []

    # 1: the close image, full bleed, with the question on a dark band
    s = fit("00a-forest-close.jpg", W)
    s = s.crop((0, 0, W, H))
    band = Image.new("RGB", (W, 330), BG)
    s.paste(band, (0, H - 330))
    d = ImageDraw.Draw(s)
    y = text(d, (M, H - 300), "Look at this image.\nHow does it make you feel?", 58, True)
    d.text((M, H - 70), "AI-generated image  ·  Data 4 The People", font=font(26, True), fill=MUTED)
    d.text((W - M, H - 70), f"1 / {n}   swipe", font=font(26), fill=CORAL, anchor="ra")
    slides.append(s)

    s, d = base(2, n)
    y = text(d, (M, 330), "Joyous? Peaceful? Calm?\nMaybe a bit jealous?", 68, True)
    text(d, (M, y + 60), "Notice the story your mind just built about this woman's hike, or her vacation, or her life.", 46, fill=INK)
    slides.append(s)

    s, d = base(3, n)
    y = text(d, (M, 150), "Now pan to the right.", 68, True)
    im = fit("00b-forest-wide.jpg", W)
    s.paste(im, (0, y + 60))
    text(d, (M, y + 60 + im.height + 60), "It is a completely different story.", 52, True, fill=CORAL)
    slides.append(s)

    s, d = base(4, n)
    y = text(d, (M, 300), "We are storytelling machines.", 68, True)
    text(d, (M, y + 60), "Our minds want stories. Feed them incomplete information and they will happily build a whole story out of it.", 46)
    slides.append(s)

    s, d = base(5, n)
    y = text(d, (M, 130), "Now consider these two data points.", 58, True)
    im = fit("00c-two-national-figures.png", W)
    s.paste(im, (0, y + 50))
    text(d, (M, y + 50 + im.height + 50), "What story does your mind create about America?", 46)
    slides.append(s)

    s, d = base(6, n)
    y = text(d, (M, 130), "Here is a third.", 58, True)
    im = fit("06-two-readings.png", W)
    s.paste(im, (0, y + 50))
    text(d, (M, y + 50 + im.height + 50),
         f"In the typical area, the median wage went from {r0:.0f}% of the local poverty threshold to {r1:.0f}%.", 42)
    slides.append(s)

    s, d = base(7, n)
    y = text(d, (M, 300), "The problem is not the data.", 68, True)
    y = text(d, (M, y + 30), "It is the story we create around it.", 68, True, fill=CORAL)
    text(d, (M, y + 70), "Stay vigilant. Look for more data. Build a more complete story.", 46)
    slides.append(s)

    s, d = base(8, n)
    im = fit("five-takeaways-single-income-hero-1680x1080.png", W)
    s.paste(im, (0, 0))
    y = text(d, (M, im.height + 70), "The Single Income Stress Test: five takeaways", 60, True)
    text(d, (M, y + 40), "What a $10,000 surprise does to one paycheck, in 521 U.S. areas.", 42)
    d.text((M, H - 150), "data4thepeople.com", font=font(44, True), fill=CORAL)
    slides.append(s)

    for i, s in enumerate(slides, 1):
        s.save(OUT / f"carousel-{i:02d}.png")
    slides[0].save(OUT / "five-takeaways-single-income-carousel.pdf", save_all=True, append_images=slides[1:], resolution=144)
    sheet = Image.new("RGB", (W * 4 // 2, H * 2 // 2), "black")
    for i, s in enumerate(slides):
        sheet.paste(s.resize((W // 2, H // 2)), ((i % 4) * W // 2, (i // 4) * H // 2))
    sheet.save(OUT / "carousel-sheet.png")
    print("wrote", len(slides), "slides and the PDF;", (OUT / "five-takeaways-single-income-carousel.pdf").stat().st_size // 1000, "KB")


if __name__ == "__main__":
    main()
