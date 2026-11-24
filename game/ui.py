"""Reusable, racing-themed Tkinter widgets and drawing helpers."""
import tkinter as tk
import tkinter.font as tkfont

from config import settings as S

_family = {"ui": "TkDefaultFont", "mono": "TkFixedFont", "display": "TkDefaultFont"}


# ------------------------------------------------------------------
# fonts and colours
# ------------------------------------------------------------------
def init_fonts(root):
    """Pick the best installed font family for each role (call once after Tk())."""
    try:
        available = set(tkfont.families(root))
    except tk.TclError:
        available = set()

    def pick(candidates, default):
        for name in candidates:
            if name in available:
                return name
        return default

    _family["ui"] = pick(S.FONT_UI, "TkDefaultFont")
    _family["mono"] = pick(S.FONT_MONO, "TkFixedFont")
    _family["display"] = pick(S.FONT_DISPLAY, _family["ui"])


def font(size=11, bold=False, italic=False, kind="ui"):
    style = " ".join(s for s, on in (("bold", bold), ("italic", italic)) if on) or "normal"
    return (_family[kind], size, style)


def _rgb(color):
    c = color.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    a, b = _rgb(c1), _rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(color, f):
    """Lighten (f > 0) or darken (f < 0) a hex colour."""
    return mix(color, "#ffffff", f) if f >= 0 else mix(color, "#000000", -f)


# ------------------------------------------------------------------
# canvas drawing helpers
# ------------------------------------------------------------------
def vgradient(canvas, x0, y0, x1, y1, c1, c2, step=3, tag="bg"):
    n = max(1, (y1 - y0) // step)
    for i in range(n + 1):
        canvas.create_rectangle(x0, y0 + i * step, x1, y0 + (i + 1) * step,
                                fill=mix(c1, c2, i / n), outline="", tags=tag)


def hgradient(canvas, x0, y0, x1, y1, c1, c2, step=4, tag="bg"):
    n = max(1, (x1 - x0) // step)
    for i in range(n + 1):
        canvas.create_rectangle(x0 + i * step, y0, x0 + (i + 1) * step, y1,
                                fill=mix(c1, c2, i / n), outline="", tags=tag)


def chamfer(x0, y0, x1, y1, c):
    """Rectangle with two cut corners (top-left, bottom-right): a racing look."""
    return [x0 + c, y0, x1, y0, x1, y1 - c, x1 - c, y1, x0, y1, x0, y0 + c]


def checker(canvas, x, y, cols, rows, size, dark="#111318", light="#ffffff", tag=""):
    for r in range(rows):
        for c in range(cols):
            fill = light if (r + c) % 2 == 0 else dark
            canvas.create_rectangle(x + c * size, y + r * size,
                                    x + (c + 1) * size, y + (r + 1) * size,
                                    fill=fill, outline="", tags=tag)


def draw_flag(canvas, x, y, size=44, tag=""):
    """Small chequered flag on a pole (replaces the emoji for a consistent look)."""
    canvas.create_line(x, y + size + 12, x, y - 4, fill="#cfd6e4", width=3, tags=tag)
    cell = size // 4
    checker(canvas, x + 2, y, 5, 4, cell, tag=tag)
    canvas.create_rectangle(x + 2, y, x + 2 + 5 * cell, y + 4 * cell,
                            outline=S.BORDER, tags=tag)


# ------------------------------------------------------------------
# containers
# ------------------------------------------------------------------
def card(parent, bg=S.PANEL, padx=22, pady=16, border=S.BORDER):
    """A panel with a 1 px border. Returns (outer_frame, inner_frame)."""
    outer = tk.Frame(parent, bg=border)
    inner = tk.Frame(outer, bg=bg, padx=padx, pady=pady)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    return outer, inner


def make_header(parent, title, subtitle=""):
    """Top banner: gradient, red accent bar, title/subtitle and a chequered strip."""
    height = 62
    c = tk.Canvas(parent, height=height, bg=S.BG, highlightthickness=0)
    c.pack(fill="x", padx=25, pady=(12, 4))

    def redraw(_event=None):
        try:
            w = max(c.winfo_width(), 400)
            c.delete("all")
            hgradient(c, 0, 0, w, height, "#1a2130", "#0e121a")
            c.create_rectangle(0, 0, 6, height, fill=S.RACE_RED, outline="")
            c.create_polygon(6, 0, 16, 0, 6, height, fill=S.RACE_RED, outline="")
            c.create_text(30, 24 if subtitle else height // 2, text=title, anchor="w",
                          fill=S.TEXT, font=font(22, True, True, "display"))
            if subtitle:
                c.create_text(31, 47, text=subtitle, anchor="w", fill=S.MUTED, font=font(10))
            checker(c, w - 90, 12, 9, 2, 10, dark="#0a0c11", light="#cfd6e4")
            c.create_line(0, height - 1, 160, height - 1, fill=S.RACE_RED, width=2)
            c.create_line(160, height - 1, w, height - 1, fill=S.BORDER)
        except tk.TclError:
            pass

    c.bind("<Configure>", redraw)
    redraw()
    return c


# ------------------------------------------------------------------
# clickable canvas controls (support .config(state=...) and ["state"])
# ------------------------------------------------------------------
class _Clickable(tk.Canvas):
    def __init__(self, parent, command, width, height):
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self._command = command
        self._state = "normal"
        self._hover = False
        self._pressed = False
        self._cw = width
        self._ch = height
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_configure)

    # -- state handling --
    def configure(self, cnf=None, **kw):
        if "state" in kw:
            self._state = kw.pop("state")
            super().configure(cursor="hand2" if self._state == "normal" else "arrow")
        for key in ("text", "command"):
            if key in kw:
                setattr(self, "_" + key, kw.pop(key))
        if cnf or kw:
            super().configure(cnf, **kw)
        self._safe_draw()

    config = configure

    def cget(self, key):
        if key == "state":
            return self._state
        return super().cget(key)

    __getitem__ = cget

    # -- events --
    def _on_configure(self, event):
        self._cw, self._ch = event.width, event.height
        self._safe_draw()

    def _on_enter(self, _e):
        self._hover = True
        self._safe_draw()

    def _on_leave(self, _e):
        self._hover = False
        self._pressed = False
        self._safe_draw()

    def _on_press(self, _e):
        if self._state == "normal":
            self._pressed = True
            self._safe_draw()

    def _on_release(self, e):
        was_pressed = self._pressed
        self._pressed = False
        self._safe_draw()
        inside = 0 <= e.x <= self._cw and 0 <= e.y <= self._ch
        if was_pressed and inside and self._state == "normal" and self._command:
            self._command()   # may rebuild the screen: nothing touches self afterwards

    def _safe_draw(self):
        try:
            self.delete("all")
            self._draw()
        except tk.TclError:
            pass

    def _draw(self):  # pragma: no cover - overridden
        raise NotImplementedError


class RaceButton(_Clickable):
    """Chamfered, shadowed button with hover/press feedback."""

    STYLES = {
        "primary": (S.RACE_RED, S.TEXT),
        "success": (S.GREEN, S.BG),
        "accent": (S.ACCENT, S.BG),
        "danger": (shade(S.RED, -0.35), S.TEXT),
        "neutral": (S.PANEL2, S.TEXT),
    }

    def __init__(self, parent, text, command, width=260, height=46, style="neutral", size=11):
        self._text = text
        self._style = style
        self._size = size
        super().__init__(parent, command, width, height + 4)
        self._safe_draw()

    def _draw(self):
        w, h = self._cw, self._ch - 4
        face, fg = self.STYLES[self._style]
        outline = S.BORDER if self._style == "neutral" else shade(face, 0.25)
        if self._state != "normal":
            face, fg, outline = "#171c27", "#5b667a", "#222a39"
        elif self._pressed:
            face = shade(face, -0.15)
        elif self._hover:
            face = shade(face, 0.16)
        dy = 2 if (self._pressed and self._state == "normal") else 0
        c = 10
        self.create_polygon(chamfer(2, 3 + dy, w - 1, h + 3, c), fill="#05070a", outline="")
        self.create_polygon(chamfer(1, 0 + dy, w - 2, h - 1 + dy, c), fill=face, outline=outline)
        if self._state == "normal":
            self.create_line(c + 2, 2 + dy, w - 4, 2 + dy, fill=shade(face, 0.3))
        self.create_text(w // 2, h // 2 + dy, text=self._text, fill=fg,
                         font=font(self._size, True))


class OptionButton(_Clickable):
    """Multiple-choice answer: lettered badge + text. Can be marked correct/wrong."""

    def __init__(self, parent, letter, text, command, height=44):
        self._letter = letter
        self._text = text
        self._mark = None
        super().__init__(parent, command, 400, height)
        self._safe_draw()

    def mark(self, kind):
        self._mark = kind
        self._safe_draw()

    def _draw(self):
        w, h = self._cw, self._ch
        face, border, badge, badge_fg, fg = S.PANEL2, S.BORDER, S.BG, S.ACCENT, S.TEXT
        badge = shade(S.ACCENT, -0.55)
        if self._mark == "correct":
            face, border, badge, badge_fg = "#14301f", S.GREEN, S.GREEN, S.BG
        elif self._mark == "wrong":
            face, border, badge, badge_fg = "#3a1420", S.RED, S.RED, S.BG
        elif self._state != "normal":
            fg, badge, badge_fg, border = "#6d788c", "#222a39", "#6d788c", "#232b3a"
            face = "#161b26"
        elif self._hover:
            face, border, badge, badge_fg = shade(S.PANEL2, 0.08), S.ACCENT, S.ACCENT, S.BG
        if self._pressed and self._state == "normal":
            face = shade(face, -0.15)
        self.create_polygon(chamfer(1, 1, w - 2, h - 2, 9), fill=face, outline=border, width=1)
        self.create_polygon(chamfer(8, 8, 36, h - 9, 5), fill=badge, outline="")
        self.create_text(22, h // 2, text=self._letter, fill=badge_fg, font=font(11, True))
        self.create_text(50, h // 2, text=self._text, anchor="w", fill=fg, font=font(11))


# ------------------------------------------------------------------
# dashboard stat card
# ------------------------------------------------------------------
class StatCard(tk.Frame):
    """Label + value with an optional progress bar or pip row underneath."""

    def __init__(self, parent, label, value, color=S.ACCENT, mode="bar"):
        super().__init__(parent, bg=S.PANEL2, highlightbackground=S.BORDER, highlightthickness=1)
        self._color = color
        self._mode = mode
        self._frac = 0.0
        self._pips = (0, 3)
        tk.Frame(self, bg=color, height=3).pack(fill="x")
        tk.Label(self, text=label, font=font(8, True), fg=S.MUTED, bg=S.PANEL2).pack(pady=(6, 0))
        self.value = tk.Label(self, text=value, font=font(15, True, kind="display"),
                              fg=S.TEXT, bg=S.PANEL2)
        self.value.pack()
        self.bar = None
        if mode in ("bar", "pips"):
            self.bar = tk.Canvas(self, width=10, height=8, bg=S.PANEL2, highlightthickness=0)
            self.bar.pack(fill="x", padx=14, pady=(2, 8))
            self.bar.bind("<Configure>", lambda e: self._draw_bar())
        else:
            tk.Frame(self, bg=S.PANEL2, height=8).pack(pady=(2, 8))

    def set(self, text, frac=None, color=None, pips=None):
        try:
            self.value.config(text=text)
            if frac is not None:
                self._frac = max(0.0, min(1.0, frac))
            if pips is not None:
                self._pips = pips
            if color is not None:
                self._color = color
            self._draw_bar()
        except tk.TclError:
            pass

    def _draw_bar(self):
        if not self.bar:
            return
        c = self.bar
        w = max(c.winfo_width(), 20)
        c.delete("all")
        if self._mode == "pips":
            have, total = self._pips
            gap = 6
            pw = (w - gap * (total - 1)) / total
            for i in range(total):
                x0 = i * (pw + gap)
                c.create_rectangle(x0, 1, x0 + pw, 7, outline="",
                                   fill=self._color if i < have else "#2a3244")
        else:
            c.create_rectangle(0, 1, w, 7, fill="#2a3244", outline="")
            c.create_rectangle(0, 1, w * self._frac, 7, fill=self._color, outline="")
            c.create_rectangle(0, 1, w * self._frac, 3, fill=shade(self._color, 0.35), outline="")
