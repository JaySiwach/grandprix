"""Central configuration: window, colours, track geometry and asset paths.

All paths are built relative to the project folder, so the game runs from
any working directory.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images")
SAVE_FILE = os.path.join(BASE_DIR, "pygp_save.json")

# ---------- window ----------
WIDTH, HEIGHT = 1180, 720
MIN_WIDTH, MIN_HEIGHT = 1000, 650
TITLE = "Python Grand Prix"

# ---------- palette ----------
BG = "#0b0e14"
PANEL = "#141a24"
PANEL2 = "#1d2431"
BORDER = "#2b3446"
CODE_BG = "#0d1118"
TEXT = "#f4f7fb"
MUTED = "#9aa6ba"
ACCENT = "#00d4ff"
GREEN = "#37d67a"
RED = "#ff5570"
YELLOW = "#ffd166"
PURPLE = "#9b7bff"
RACE_RED = "#e10600"
TRACK = "#303744"
WHITE = "#ffffff"

# ---------- fonts (first installed family wins) ----------
FONT_UI = ["Segoe UI", "SF Pro Text", "Helvetica Neue", "Ubuntu", "DejaVu Sans", "Arial"]
FONT_MONO = ["Cascadia Mono", "Consolas", "Menlo", "DejaVu Sans Mono", "Courier New"]
FONT_DISPLAY = ["Bahnschrift", "Segoe UI", "Helvetica Neue", "Ubuntu", "DejaVu Sans", "Arial"]

# ---------- track geometry (pixels) ----------
TRACK_H = 240          # canvas height of the race strip
BANNER_H = 34          # checkpoint-label banner above the road
KERB = 6               # kerb thickness
LANE_H = 46            # one lane per car (player + 3 AI)
LANES = 4
ROAD_TOP = BANNER_H + KERB
ROAD_BOT = ROAD_TOP + LANE_H * LANES
START_X = 28           # chequered start line
CAR_LEFT = 112         # car centre at 0 % progress
CAR_RIGHT = 88         # distance from the right edge at 100 % progress
GATE_OFFSET = 34       # a checkpoint gate sits just ahead of the car centre
MIN_TRACK_WIDTH = 900  # same minimum drawing width as the original

# ---------- cars ----------
CAR_FILES = {
    "player": os.path.join(IMAGES_DIR, "player_car.png"),
    "ai0": os.path.join(IMAGES_DIR, "ai_cars", "car_1_red.png"),
    "ai1": os.path.join(IMAGES_DIR, "ai_cars", "car_2_yellow.png"),
    "ai2": os.path.join(IMAGES_DIR, "ai_cars", "car_3_purple.png"),
}
# colours used for the vector fallback car and the number tags
CAR_COLORS = {"player": ACCENT, "ai0": "#ff3b57", "ai1": "#ffc02e", "ai2": PURPLE}
