#!/usr/bin/env python3
"""Build the KDP covers as JPG: Kindle, paperback and hardcover, in EN, FR and PL.

Usage: ./build_covers.py            (needs Pillow, numpy, weasyprint, pdftoppm)
Front art: src/front-art-remix.jpg, with no lettering on it; the title and subtitle are set here.
Print sizes follow KDP's cover rules (white paper, 0.002252 in per page) and the page counts are read
from the interior PDFs that build_interior.sh makes, so run that first.
"""
import subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = Path.home() / ".local/share/fonts/free-font-library/google-fonts/fonts-HEAD/ofl"
MONT = str(FONTS / "montserrat/Montserrat[wght].ttf")
DPI = 300
ART = "src/front-art-remix.jpg"

def pages(lang, fmt):
    pdf = HERE / f"{fmt}/Rakszawa-Wisconsin-{lang}-{fmt}-interior.pdf"
    out = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
    return int(out.split("Pages:")[1].split()[0])

TEXT = {
 "EN": dict(sub="WHY DOES BOBER DRINK BEER?",
  tag="Six centuries, one wall, and a can that lies about where it comes from.",
  body=["Łukasz Bober is a Polish mixed-media artist, musician and muralist. He paints massive walls into colourful life, he loves books, and somewhere around half past three in the afternoon he opens a can of Pabst Blue Ribbon.",
        "This book takes the question “why?” far too seriously, and finds six answers. Five of them are wrong.",
        "The can was brewed in Poland, at Rakszawa in Podkarpacie. The blue ribbon commemorates a prize that was never awarded. The famous finding that alcohol makes you more creative failed its replication.",
        "So it is not an import, it is not a medal, and it is not a muse."],
  close="The beer is a receipt for time that has no invoice.",
  credit="Research and writing by Claude ‘Opus’ Five. Guided by Jason ‘phr0zt’ Moss."),
 "FR": dict(sub="POURQUOI BOBER BOIT-IL DE LA BIÈRE ?",
  tag="Six siècles, un mur, et une canette qui ment sur ses origines.",
  body=["Łukasz Bober est un artiste polonais aux techniques mixtes, musicien et muraliste. Il donne vie et couleur à des murs immenses, il aime les livres, et vers trois heures et demie de l’après-midi il ouvre une canette de Pabst Blue Ribbon.",
        "Ce livre prend la question « pourquoi ? » beaucoup trop au sérieux, et lui trouve six réponses. Cinq d’entre elles sont fausses.",
        "La canette a été brassée en Pologne, à Rakszawa, en Podkarpacie. Le ruban bleu commémore un prix qui n’a jamais été décerné. Et la célèbre étude selon laquelle l’alcool rend plus créatif n’a pas survécu à sa réplication.",
        "Ce n’est donc ni une importation, ni une médaille, ni une muse."],
  close="La bière est un reçu pour du temps qui n’a pas de facture.",
  credit="Recherche et écriture : Claude « Opus » Five. Sous la direction de Jason « phr0zt » Moss."),
 "PL": dict(sub="DLACZEGO BOBER PIJE PIWO?",
  tag="Sześć wieków, jedna ściana i puszka, która kłamie o swoim pochodzeniu.",
  body=["Łukasz Bober jest polskim artystą mixed media, muzykiem i muralistą. Zamienia ogromne ściany w kolor i życie, kocha książki, a gdzieś koło wpół do czwartej po południu otwiera puszkę Pabst Blue Ribbon.",
        "Ta książka traktuje pytanie „dlaczego?” o wiele za poważnie i znajduje sześć odpowiedzi. Pięć z nich jest błędnych.",
        "Puszkę uwarzono w Polsce, w Rakszawie na Podkarpaciu. Niebieska wstęga upamiętnia nagrodę, której nigdy nie przyznano. A słynne badanie, według którego alkohol zwiększa kreatywność, nie przetrwało replikacji.",
        "Więc to nie import, nie medal i nie muza."],
  close="Piwo jest paragonem za czas, na który nie ma faktury.",
  credit="Badania i tekst: Claude „Opus” Five. Prowadzenie: Jason „phr0zt” Moss."),
}

def px(inch): return round(inch * DPI)

def subtitle(im, lang, cx, cy, maxw, size, s=None, weight="Bold", track=0.13):
    """Set the subtitle in this language (or the line s), centred on (cx, cy), shrunk until it fits
    maxw. All px. Returns the font size used."""
    s = s or TEXT[lang]["sub"]; size = round(size)
    while True:
        f = ImageFont.truetype(MONT, size); f.set_variation_by_name(weight)
        gap = track * size
        adv = [f.getlength(c) for c in s]
        tw = sum(adv) + gap * (len(s) - 1)
        if tw <= maxw: break
        size -= 1
    layer = Image.new("L", im.size, 0); d = ImageDraw.Draw(layer)
    x = cx - tw / 2
    for c, a in zip(s, adv):
        d.text((x, cy), c, font=f, fill=255, anchor="lm"); x += a + gap
    shadow = Image.new("L", im.size, 0); shadow.paste(layer, (round(size * .04), round(size * .08)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * .14)).point(lambda v: int(v * .75))
    im.paste((0, 0, 0), mask=shadow); im.paste((255, 255, 255), mask=layer)
    return size

def title(im, lang, cx, top, maxw):
    """Title in two lines with the subtitle under it, centred on cx, in a box maxw wide. All px."""
    ts = subtitle(im, lang, cx, top + maxw * .09, maxw, maxw * .24, s="RAKSZAWA,", weight="ExtraBold", track=0.02)
    y = top + maxw * .09
    subtitle(im, lang, cx, y + ts * 1.08, maxw, ts, s="WISCONSIN", weight="ExtraBold", track=0.02)
    subtitle(im, lang, cx, y + ts * 2.0, maxw, ts * 0.27)

def canvas(W, H, x0, ax, ay, aw, ah):
    """Full wrap: the art at (ax, ay), mirrored where it does not reach the edge. Everything left of
    the front fold x0 (spine + back) is the front mirrored, blurred and darkened."""
    a = np.asarray(Image.open(HERE / ART).convert("RGB").resize((aw, ah), Image.LANCZOS))
    t, r, b = max(0, ay), max(0, W - ax - aw), max(0, H - ay - ah)
    a = np.pad(a, ((t, b), (0, r), (0, 0)), mode="reflect")
    oy = -ay if ay < 0 else 0
    front = Image.fromarray(a).crop((0, oy, W - x0, oy + H))
    if not x0: return front
    back = front.transpose(Image.FLIP_LEFT_RIGHT).resize((x0, H)).filter(ImageFilter.GaussianBlur(60))
    back = Image.blend(back, Image.new("RGB", back.size, (14, 16, 18)), 0.66)
    out = Image.new("RGB", (W, H)); out.paste(back, (0, 0)); out.paste(front, (x0, 0))
    return out

CSS = """
@page {{ size: {W}in {H}in; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
body {{ width: {W}in; height: {H}in; position: relative; color: #f3f0ea;
  background: url({bg}) 0 0 / {W}in {H}in no-repeat; font-family: "Source Serif 4", Georgia, serif; }}
.back {{ position: absolute; left: {bx}in; top: {by}in; width: {bw}in; }}
.tag {{ font: 700 10.5pt/1.45 Montserrat, sans-serif; letter-spacing: .09em; text-transform: uppercase; margin: 0 0 .3in; }}
.rule {{ width: .6in; border-top: 2pt solid #d9a441; margin: 0 0 .3in; }}
.back p.b {{ font-size: {fs}pt; line-height: 1.5; margin: 0 0 .8em; }}
.close {{ font: 700 12.5pt/1.4 Montserrat, sans-serif; margin: .3in 0 0; }}
.foot {{ position: absolute; left: {bx}in; top: {fy}in; width: {fw}in; }}
.author {{ font: 700 10.5pt/1.2 Montserrat, sans-serif; letter-spacing: .1em; text-transform: uppercase; margin: 0 0 .08in; }}
.credit {{ font: 400 6.6pt/1.4 Montserrat, sans-serif; margin: 0; opacity: .85; }}
.spine {{ position: absolute; transform: rotate(90deg); text-align: center; white-space: nowrap;
  font: 700 7.5pt/1 Montserrat, sans-serif; letter-spacing: .12em; text-transform: uppercase; }}
.spine span {{ margin-left: .5in; font-weight: 500; }}
"""

def render(name, bg_img, W, H, lang=None, back=None, spine=None, tmp=None):
    """Typeset the back cover (and spine) over the background, then rasterise to an exact-size JPG."""
    out = HERE / name; out.parent.mkdir(exist_ok=True)
    if not back:
        bg_img.save(out, quality=95, subsampling=0, dpi=(DPI, DPI)); return out
    bg = Path(tmp) / "bg.jpg"; bg_img.save(bg, quality=97, subsampling=0)
    t = TEXT[lang]; bx, by, bw, fy, fs = back
    sp = ""
    if spine:
        cx, sw = spine
        sp = (f'<div class="spine" style="left:{cx - H / 2:.4f}in;top:{H / 2 - sw / 2:.4f}in;width:{H}in;'
              f'height:{sw:.4f}in;line-height:{sw:.4f}in">Rakszawa, Wisconsin<span>Jason ’phr0zt’ Moss</span></div>')
    html = (f'<!DOCTYPE html><html lang="{lang.lower()}"><meta charset="utf-8"><style>'
            + CSS.format(W=W, H=H, bg=bg.name, bx=bx, by=by, bw=bw, fy=fy, fw=min(bw, 2.3), fs=fs)
            + f'</style><div class="back"><p class="tag">{t["tag"]}</p><div class="rule"></div>'
            + "".join(f'<p class="b">{p}</p>' for p in t["body"]) + f'<p class="close">{t["close"]}</p></div>'
            + f'<div class="foot"><p class="author">Jason ’phr0zt’ Moss</p><p class="credit">{t["credit"]}</p></div>{sp}</html>')
    (Path(tmp) / "c.html").write_text(html)
    subprocess.run(["weasyprint", "-q", str(Path(tmp) / "c.html"), str(Path(tmp) / "c.pdf")], check=True)
    subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=95", "-singlefile", "-scale-to-x", str(px(W)),
                    "-scale-to-y", str(px(H)), str(Path(tmp) / "c.pdf"), str(out.with_suffix(""))], check=True)
    im = Image.open(out); im.save(out, quality=95, subsampling=0, dpi=(DPI, DPI))   # stamp 300 DPI
    im.save(out.with_suffix(".pdf"), resolution=DPI, quality=95, subsampling=0)     # same image as a PDF, for KDP's print uploader
    return out

def main():
    with Image.open(HERE / ART) as r: ra = r.width / r.height
    with tempfile.TemporaryDirectory() as tmp:
        for lang in TEXT:
            # Kindle: the whole art, 2560 px tall (KDP's recommended height)
            w, h = round(2560 * ra), 2560
            bg = canvas(w, h, 0, 0, 0, w, h)
            title(bg, lang, w / 2, h * .05, w * .84)
            o = render(f"kindle/Rakszawa-Wisconsin-{lang}-kindle.jpg", bg, 0, 0)
            print(o.name, Image.open(o).size)

            # Paperback, 6 x 9 trim: 0.125 bleed | back | spine | front | 0.125 bleed, 9.25 high.
            # The art fills the front from the fold to the bleed; the title sits 0.45 in inside the trim.
            # No spine text: KDP only allows it from 79 pages.
            tw, th = 6, 9
            spine = pages(lang, "paperback") * 0.002252
            W, H = round(0.25 + 2 * tw + spine, 3), th + 0.25
            x0 = 0.125 + tw + spine
            ah = px(H); aw = max(round(ah * ra), px(W) - px(x0))
            bg = canvas(px(W), px(H), px(x0), px(x0), 0, aw, ah)
            title(bg, lang, px(x0 + tw / 2), px(0.125 + 0.5), px(tw - 0.9))
            o = render(f"paperback/Rakszawa-Wisconsin-{lang}-paperback-6x9.jpg", bg, W, H, lang,
                       back=(0.125 + 0.65, 0.125 + 0.8, tw - 1.3, H - 0.125 - 1.0, 10.8), tmp=tmp)
            print(o.name, Image.open(o).size, f"{W} x {H} in, spine {spine:.3f} in")

            # Hardcover (case laminate), trim 5.5 x 8.5: 0.591 wrap | board | spine | board | 0.591 wrap.
            # Board = trim + 0.197 wide, + 0.236 high; spine = paper + 0.189 for the boards.
            # The art fills the front board from the hinge outwards and is mirrored round the wrap.
            # Text must stay 0.635 in from the board edges and 0.4 in off the hinge.
            wrap, bw_, bh = 0.591, 5.5 + 0.197, 8.5 + 0.236
            spine = pages(lang, "hardcover") * 0.002252 + 0.189
            W, H = round(2 * wrap + 2 * bw_ + spine, 3), round(bh + 2 * wrap, 3)
            x0 = wrap + bw_ + spine
            ah = px(bh) + 60; aw = round(ah * ra)
            bg = canvas(px(W), px(H), px(x0), px(x0), px(wrap) - 30, aw, ah)
            sw_ = px(bw_ - 0.4 - 0.635)
            title(bg, lang, px(x0 + 0.4) + sw_ / 2, px(wrap + 0.635), sw_)
            o = render(f"hardcover/Rakszawa-Wisconsin-{lang}-hardcover-5.5x8.5.jpg", bg, W, H, lang,
                       back=(wrap + 0.75, wrap + 0.9, bw_ - 0.75 - 0.6, wrap + bh - 0.635 - 0.55, 10.2),
                       spine=(wrap + bw_ + spine / 2, spine), tmp=tmp)
            print(o.name, Image.open(o).size, f"{W} x {H} in, spine {spine:.3f} in")

if __name__ == "__main__": main()
