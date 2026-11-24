"""Generates the racing-car PNGs used by the game (needs Pillow).

Run from the project root:  python tools/generate_assets.py
The PNGs are already included in assets/images, so this is only needed
if you want to re-colour or tweak the cars.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

S = 6                      # supersampling factor
W, H = 124, 52             # final image size in pixels (includes shadow margin)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sc(pts):
    return [(x * S, y * S) for x, y in pts]


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient_fill(size, top, bottom):
    g = Image.new("RGB", size)
    d = ImageDraw.Draw(g)
    for y in range(size[1]):
        d.line([(0, y), (size[0], y)], fill=mix(top, bottom, y / max(1, size[1] - 1)))
    return g


def draw_car(main_hex, accent_hex="#ffffff"):
    main = hex_rgb(main_hex)
    light = mix(main, (255, 255, 255), 0.22)
    dark = mix(main, (0, 0, 0), 0.5)
    accent = hex_rgb(accent_hex)
    big = (W * S, H * S)
    car = Image.new("RGBA", big, (0, 0, 0, 0))
    d = ImageDraw.Draw(car)
    cy = 25  # centre line (car drawn pointing right)

    # wheels (tyre, sidewall, rim)
    def wheel(x0, x1, y0, y1):
        d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=int(2.2 * S), fill=(18, 18, 22, 255))
        d.rounded_rectangle([(x0 + 1.2) * S, (y0 + 1.2) * S, (x1 - 1.2) * S, (y1 - 1.2) * S],
                            radius=int(1.6 * S), fill=(36, 38, 46, 255))
        d.rectangle([(x0 + 3) * S, (y0 + 2.1) * S, (x1 - 3) * S, (y0 + 2.9) * S], fill=(120, 126, 140, 255))
    # suspension arms
    for x in (29, 88):
        d.line(sc([(x, cy - 10), (x, cy + 10)]), fill=(25, 25, 30, 255), width=int(1.6 * S))
    wheel(21, 40, 4, 14.5)
    wheel(21, 40, 35.5, 46)
    wheel(80, 96, 6, 15)
    wheel(80, 96, 35, 44)

    # rear wing
    d.rectangle(sc([(8, 9)])[0] + sc([(18, 41)])[0], fill=dark + (255,))
    d.rectangle(sc([(9, 10)])[0] + sc([(16, 40)])[0], fill=main + (255,))
    d.rectangle(sc([(8, 8)])[0] + sc([(19, 10)])[0], fill=(20, 20, 24, 255))
    d.rectangle(sc([(8, 40)])[0] + sc([(19, 42)])[0], fill=(20, 20, 24, 255))
    d.rectangle(sc([(13, 10)])[0] + sc([(14.2, 40)])[0], fill=dark + (255,))
    # front wing
    d.rectangle(sc([(102, 10)])[0] + sc([(113, 40)])[0], fill=dark + (255,))
    d.rectangle(sc([(104, 11.5)])[0] + sc([(112, 38.5)])[0], fill=main + (255,))
    d.rectangle(sc([(102, 8.5)])[0] + sc([(114, 10.5)])[0], fill=(20, 20, 24, 255))
    d.rectangle(sc([(102, 39.5)])[0] + sc([(114, 41.5)])[0], fill=(20, 20, 24, 255))

    # main body with vertical gradient (3-D feel)
    body_pts = [(18, 20.5), (30, 17), (42, 13.5), (56, 15), (68, 19), (82, 21.5), (106, 23.6),
                (107, 25), (106, 26.4), (82, 28.5), (68, 31), (56, 35), (42, 36.5), (30, 33), (18, 29.5)]
    mask = Image.new("L", big, 0)
    ImageDraw.Draw(mask).polygon(sc(body_pts), fill=255)
    grad = gradient_fill(big, light, dark)
    car.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(car)
    d.line(sc(body_pts + [body_pts[0]]), fill=dark + (255,), width=int(0.7 * S))

    # sidepod inlets
    for sgn in (-1, 1):
        y = cy + sgn * 8.2
        d.rounded_rectangle([48 * S, (y - 1.4) * S, 56 * S, (y + 1.4) * S], radius=int(S), fill=(15, 15, 20, 255))

    # centre racing stripe
    d.polygon(sc([(20, cy - 1.3), (70, cy - 1.3), (105, cy - 0.5), (105, cy + 0.5), (70, cy + 1.3), (20, cy + 1.3)]),
              fill=accent + (255,))
    # engine cover highlight
    d.polygon(sc([(24, cy - 4.5), (46, cy - 6), (46, cy - 3.2), (24, cy - 2.6)]), fill=light + (150,))
    # airbox
    d.ellipse(sc([(44, cy - 3.2)])[0] + sc([(53, cy + 3.2)])[0], fill=(22, 24, 30, 255))
    # cockpit + helmet
    d.ellipse(sc([(55, cy - 5)])[0] + sc([(70, cy + 5)])[0], fill=(14, 16, 22, 255))
    d.ellipse(sc([(59, cy - 3.2)])[0] + sc([(65.5, cy + 3.2)])[0], fill=accent + (255,))
    d.rectangle(sc([(62, cy - 1.8)])[0] + sc([(65.5, cy + 1.8)])[0], fill=(30, 40, 60, 255))
    # nose cone tip
    d.ellipse(sc([(102, cy - 1.4)])[0] + sc([(108, cy + 1.4)])[0], fill=accent + (255,))

    # soft shadow (offset silhouette, blurred)
    alpha = car.split()[3]
    sh = Image.new("RGBA", big, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 120), (int(1.5 * S), int(2.8 * S)), alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * S))
    out = Image.alpha_composite(sh, car)
    return out.resize((W, H), Image.LANCZOS)


CARS = {
    "player_car.png": "#00c8ff",
    "ai_cars/car_1_red.png": "#ff3b57",
    "ai_cars/car_2_yellow.png": "#ffc02e",
    "ai_cars/car_3_purple.png": "#9b6bff",
}


def main():
    for name, col in CARS.items():
        path = os.path.join(ROOT, "assets", "images", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        draw_car(col).save(path)
        print("wrote", path)


if __name__ == "__main__":
    main()
