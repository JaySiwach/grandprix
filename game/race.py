"""Racing track and car rendering.

Cars are PNG sprites from assets/images. If a sprite (or Pillow, used only for
the textured asphalt) is missing, the game falls back to vector drawing so it
never crashes because of an asset.
"""
import os
import random
import tkinter as tk

from config import settings as S
from game.game_data import RACES, TOPICS
from game.ui import checker, draw_flag, font, mix, shade, vgradient

try:  # optional: textured track background
    from PIL import Image, ImageDraw, ImageFilter, ImageTk
    PIL_OK = True
except Exception:  # Pillow (or ImageTk) not installed
    PIL_OK = False


# ------------------------------------------------------------------
# cars
# ------------------------------------------------------------------
def draw_vector_car(canvas, x, y, color, tags=()):
    """Fallback F1-style car (about 104 x 40 px), pointing right."""
    dark = shade(color, -0.5)
    tyre = "#14161b"
    # wheels
    for wx0, wx1, dy in ((-40, -22, 15), (-40, -22, -15), (18, 34, 14), (18, 34, -14)):
        canvas.create_rectangle(x + wx0, y + dy - 5, x + wx1, y + dy + 5, fill=tyre, outline="", tags=tags)
    # wings
    canvas.create_rectangle(x - 54, y - 16, x - 44, y + 16, fill=color, outline=dark, tags=tags)
    canvas.create_rectangle(x + 40, y - 14, x + 50, y + 14, fill=color, outline=dark, tags=tags)
    # body
    canvas.create_polygon(x - 44, y - 5, x - 32, y - 8, x - 20, y - 11, x - 6, y - 10, x + 6, y - 6,
                          x + 20, y - 3, x + 44, y - 1, x + 44, y + 1, x + 20, y + 3, x + 6, y + 6,
                          x - 6, y + 10, x - 20, y + 11, x - 32, y + 8, x - 44, y + 5,
                          fill=color, outline=dark, tags=tags)
    canvas.create_line(x - 42, y, x + 43, y, fill="#ffffff", width=2, tags=tags)
    canvas.create_oval(x - 6, y - 5, x + 8, y + 5, fill="#0e1016", outline="", tags=tags)
    canvas.create_oval(x - 3, y - 3, x + 4, y + 3, fill="#ffffff", outline="", tags=tags)


class CarSprites:
    """Loads the car PNGs once and draws them (with a small number tag)."""

    def __init__(self):
        self.images = {key: self._load(path) for key, path in S.CAR_FILES.items()}

    @staticmethod
    def _load(path):
        try:
            if os.path.isfile(path):
                return tk.PhotoImage(file=path)
        except tk.TclError:
            pass
        return None

    def draw(self, canvas, key, x, y, label, tags=("car",)):
        img = self.images.get(key)
        if img is not None:
            canvas.create_image(x, y, image=img, tags=tags)
        else:
            draw_vector_car(canvas, x, y, S.CAR_COLORS[key], tags)
        # number / name plate on the engine cover
        tx = x - 29
        pill_w = 12 + 6 * len(label)
        canvas.create_rectangle(tx - pill_w / 2, y - 6, tx + pill_w / 2, y + 6,
                                fill="#0c0f15", outline=S.CAR_COLORS[key], tags=tags)
        canvas.create_text(tx, y, text=label, fill=S.TEXT, font=font(7, True), tags=tags)


# ------------------------------------------------------------------
# race track
# ------------------------------------------------------------------
class TrackRenderer:
    """Draws the road, gates and all four cars on a canvas."""

    def __init__(self, canvas, cars):
        self.canvas = canvas
        self.cars = cars
        self._backgrounds = {}

    # -- geometry (shared by cars, gates and labels) --
    @staticmethod
    def x_of(progress, width):
        return S.CAR_LEFT + progress * (width - S.CAR_LEFT - S.CAR_RIGHT)

    @classmethod
    def gate_x(cls, i, width):
        return cls.x_of((i + 1) / 10, width) + S.GATE_OFFSET

    @staticmethod
    def lane_y(lane):
        return S.ROAD_TOP + S.LANE_H * (lane + 0.5)

    # -- drawing --
    def draw(self, race_index, challenge_index, ai, player_progress=None):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), S.MIN_TRACK_WIDTH)
        self._draw_background(w)

        # Ten track markers represent the ten correct answers needed to finish.
        for i in range(10):
            gx = self.gate_x(i, w)
            if i < round((player_progress or 0) * 10):
                color, weight = "#4ea77a", False
            else:
                color, weight = S.MUTED, True
            c.create_text(gx, S.BANNER_H // 2, text=str(i + 1), fill=color,
                          font=font(8, weight))

        # Player progress is earned by correct answers: ten correct answers reach the finish line.
        if player_progress is None:
            player_progress = challenge_index / 10
        self.cars.draw(c, "player", self.x_of(player_progress, w), self.lane_y(0), "YOU")
        for i, car in enumerate(ai):
            x = self.x_of(min(1, car["progress"]), w)
            self.cars.draw(c, "ai%d" % i, x, self.lane_y(i + 1), str(i + 1))

    # -- background --
    def _draw_background(self, w):
        photo = self._textured(w) if PIL_OK else None
        if photo is not None:
            self.canvas.create_image(0, 0, image=photo, anchor="nw")
        else:
            self._vector_background(w)

    def _textured(self, w):
        if w not in self._backgrounds:
            if len(self._backgrounds) > 6:
                self._backgrounds.clear()
            try:
                self._backgrounds[w] = ImageTk.PhotoImage(render_track_image(w, S.TRACK_H))
            except Exception:
                self._backgrounds[w] = None
        return self._backgrounds[w]

    def _vector_background(self, w):
        c = self.canvas
        h = S.TRACK_H
        vgradient(c, 0, 0, w, h, "#12281c", "#0e1d15")
        c.create_rectangle(0, 0, w, S.BANNER_H, fill="#0c0f15", outline="")
        c.create_line(0, S.BANNER_H, w, S.BANNER_H, fill=S.RACE_RED)
        for x in range(0, w, 24):
            col = S.RACE_RED if (x // 24) % 2 == 0 else S.WHITE
            c.create_rectangle(x, S.BANNER_H, x + 24, S.ROAD_TOP, fill=col, outline="")
            c.create_rectangle(x, S.ROAD_BOT, x + 24, S.ROAD_BOT + S.KERB, fill=col, outline="")
        c.create_rectangle(0, S.ROAD_TOP, w, S.ROAD_BOT, fill=S.TRACK, outline="")
        c.create_line(0, S.ROAD_TOP + 2, w, S.ROAD_TOP + 2, fill="#d7dce6")
        c.create_line(0, S.ROAD_BOT - 3, w, S.ROAD_BOT - 3, fill="#d7dce6")
        for lane in range(1, S.LANES):
            y = S.ROAD_TOP + lane * S.LANE_H
            for x in range(0, w, 40):
                c.create_line(x, y, x + 22, y, fill="#5d6677")
        for i in range(10):
            gx = self.gate_x(i, w)
            c.create_line(gx, S.BANNER_H, gx, S.ROAD_BOT, fill="#697386", dash=(4, 6))
        checker(c, S.START_X, S.ROAD_TOP, 2, S.LANE_H * S.LANES // 8, 8)
        checker(c, int(self.gate_x(9, w)) - 8, S.ROAD_TOP, 2, S.LANE_H * S.LANES // 8, 8)


def render_track_image(w, h):
    """Photo-like top-down track strip: grass, kerbs, textured asphalt, markings."""
    rnd = random.Random(11)
    road_h = S.ROAD_BOT - S.ROAD_TOP
    base = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(base)

    # grass with mowing stripes
    for y in range(h):
        d.line([(0, y), (w, y)], fill=mix("#17351f", "#0e2116", y / h) + "ff")
    stripes = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for x in range(0, w, 64):
        if (x // 64) % 2 == 0:
            sd.rectangle([x, 0, x + 63, h], fill=(255, 255, 255, 9))
    base = Image.alpha_composite(base, stripes)
    d = ImageDraw.Draw(base)

    # label banner (pit wall)
    d.rectangle([0, 0, w, S.BANNER_H], fill=(10, 12, 18, 255))
    d.line([(0, S.BANNER_H - 1), (w, S.BANNER_H - 1)], fill=(225, 6, 0, 255), width=2)

    # asphalt: gradient + grain
    road = Image.new("RGB", (w, road_h))
    rd = ImageDraw.Draw(road)
    for y in range(road_h):
        t = abs((y / road_h) - 0.5) * 2
        rd.line([(0, y), (w, y)], fill=mix("#2b313d", "#1c212b", t))
    grain = Image.effect_noise((w, road_h), 26)
    road = Image.blend(road, Image.merge("RGB", (grain, grain, grain)), 0.14)
    base.paste(road, (0, S.ROAD_TOP))

    # rubbered-in racing lines + oil patches
    marks = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    md = ImageDraw.Draw(marks)
    for lane in range(S.LANES):
        cy = S.ROAD_TOP + S.LANE_H * lane + S.LANE_H // 2
        for off in (-7, 7):
            md.line([(0, cy + off), (w, cy + off)], fill=(0, 0, 0, 46), width=5)
    for _ in range(max(6, w // 140)):
        x, y = rnd.randint(0, w), rnd.randint(S.ROAD_TOP + 6, S.ROAD_BOT - 6)
        md.ellipse([x, y, x + rnd.randint(30, 70), y + rnd.randint(5, 10)], fill=(0, 0, 0, 34))
    base = Image.alpha_composite(base, marks.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(base)

    # kerbs (red / white) with a shaded inner edge
    for x in range(0, w, 24):
        col = (225, 6, 0, 255) if (x // 24) % 2 == 0 else (240, 242, 247, 255)
        d.rectangle([x, S.BANNER_H, x + 23, S.ROAD_TOP - 1], fill=col)
        d.rectangle([x, S.ROAD_BOT, x + 23, S.ROAD_BOT + S.KERB - 1], fill=col)
    d.line([(0, S.ROAD_TOP - 1), (w, S.ROAD_TOP - 1)], fill=(0, 0, 0, 120))
    d.line([(0, S.ROAD_BOT + S.KERB), (w, S.ROAD_BOT + S.KERB)], fill=(0, 0, 0, 160))

    # barrier along the bottom
    by = S.ROAD_BOT + S.KERB + 3
    d.rectangle([0, by, w, h], fill=(26, 30, 40, 255))
    for x in range(0, w, 120):
        d.rectangle([x + 4, by + 2, x + 62, by + 7], fill=(0, 150, 190, 255))
        d.rectangle([x + 66, by + 2, x + 114, by + 7], fill=(200, 205, 215, 255))

    # painted markings: edge lines, dashed lane lines, gates
    paint = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(paint)
    pd.line([(0, S.ROAD_TOP + 2), (w, S.ROAD_TOP + 2)], fill=(235, 238, 245, 220), width=2)
    pd.line([(0, S.ROAD_BOT - 3), (w, S.ROAD_BOT - 3)], fill=(235, 238, 245, 220), width=2)
    for lane in range(1, S.LANES):
        y = S.ROAD_TOP + lane * S.LANE_H
        for x in range(0, w, 44):
            pd.line([(x, y), (x + 24, y)], fill=(235, 238, 245, 80), width=2)
    for i in range(9):  # the 10th gate is the chequered finish line
        gx = int(TrackRenderer.gate_x(i, w))
        for y in range(S.BANNER_H, S.ROAD_BOT, 12):
            pd.line([(gx, y), (gx, y + 6)], fill=(180, 190, 208, 90), width=1)
    base = Image.alpha_composite(base, paint)
    d = ImageDraw.Draw(base)

    def chequered(x, width_cells):
        size = 8
        rows = (S.ROAD_BOT - S.ROAD_TOP) // size
        for r in range(rows):
            for cidx in range(width_cells):
                col = (245, 246, 250, 255) if (r + cidx) % 2 == 0 else (14, 15, 19, 255)
                d.rectangle([x + cidx * size, S.ROAD_TOP + r * size,
                             x + (cidx + 1) * size - 1, S.ROAD_TOP + (r + 1) * size - 1], fill=col)

    chequered(S.START_X, 2)
    chequered(int(TrackRenderer.gate_x(9, w)) - 8, 2)

    # soft vignette on the left/right ends
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(50):
        a = int(110 * (1 - i / 50) ** 2)
        vd.line([(i, 0), (i, h)], fill=(0, 0, 0, a))
        vd.line([(w - 1 - i, 0), (w - 1 - i, h)], fill=(0, 0, 0, a))
    return Image.alpha_composite(base, vig).convert("RGB")


# ------------------------------------------------------------------
# menu hero banner
# ------------------------------------------------------------------
def draw_hero(canvas, cars, w, h):
    """Menu banner: title, tagline and the four cars lined up on a strip of track."""
    canvas.delete("all")
    vgradient(canvas, 0, 0, w, h, "#18202e", "#0b0e14")
    # diagonal speed stripes
    for k, col in enumerate(("#2a0d10", "#1b2230", "#1f0a0d")):
        x = w * 0.62 + k * 70
        canvas.create_polygon(x, 0, x + 38, 0, x - 120, h, x - 158, h, fill=col, outline="")
    canvas.create_polygon(w * 0.62 + 210, 0, w * 0.62 + 222, 0, w * 0.62 + 64, h, w * 0.62 + 52, h,
                          fill=S.RACE_RED, outline="")

    cx = w // 2
    draw_flag(canvas, cx - 14, 14, size=28)
    f_title = font(38, True, True, "display")
    t1, t2 = "PYTHON ", "GRAND PRIX"
    from tkinter import font as tkfont
    f = tkfont.Font(font=f_title)
    total = f.measure(t1 + t2)
    x0 = cx - total // 2
    canvas.create_text(x0 + 3, 83, text=t1, anchor="w", fill="#000000", font=f_title)
    canvas.create_text(x0 + 3 + f.measure(t1), 83, text=t2, anchor="w", fill="#000000", font=f_title)
    canvas.create_text(x0, 80, text=t1, anchor="w", fill=S.ACCENT, font=f_title)
    canvas.create_text(x0 + f.measure(t1), 80, text=t2, anchor="w", fill=S.TEXT, font=f_title)
    canvas.create_text(cx, 118, text="RACE.  CODE.  UPGRADE.  BECOME THE PYTHON CHAMPION.",
                       fill=S.YELLOW, font=font(10, True))
    canvas.create_text(cx, 140, text="A coding-racing championship built around 50 Python built-ins",
                       fill=S.MUTED, font=font(11))

    # strip of track with the cars on the grid
    top, bottom = 156, h - 6
    canvas.create_rectangle(0, top, w, bottom, fill="#222834", outline="")
    for x in range(0, w, 24):
        col = S.RACE_RED if (x // 24) % 2 == 0 else S.WHITE
        canvas.create_rectangle(x, top - 5, x + 24, top, fill=col, outline="")
        canvas.create_rectangle(x, bottom, x + 24, bottom + 5, fill=col, outline="")
    for x in range(0, w, 60):
        canvas.create_rectangle(x, (top + bottom) // 2 - 1, x + 30, (top + bottom) // 2 + 1,
                                fill="#4b5465", outline="")
    cy = (top + bottom) // 2
    for key, label, frac in (("ai2", "3", 0.20), ("ai1", "2", 0.38), ("ai0", "1", 0.56),
                             ("player", "YOU", 0.78)):
        cars.draw(canvas, key, int(w * frac), cy, label)
