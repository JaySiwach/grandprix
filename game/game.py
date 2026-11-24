"""Game state, rules and screen flow.

The rules (scoring, speed/fuel/grip/boost, AI progress, penalties) are the
original game's, line for line; only the presentation moved to ui.py / race.py.
"""
import random
import time
import tkinter as tk
from tkinter import simpledialog, messagebox

from config import settings as S
from game import ui
from game.game_data import RACES
from game.leaderboard import load_scores, save_result, save_race_result
from game.questions import pick_question, build_question_deck
from game.race import CarSprites, TrackRenderer, draw_hero
from game.ui import OptionButton, RaceButton, StatCard, card, font, make_header


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title(S.TITLE)
        self.root.geometry(f"{S.WIDTH}x{S.HEIGHT}")
        self.root.minsize(S.MIN_WIDTH, S.MIN_HEIGHT)
        self.root.configure(bg=S.BG)
        ui.init_fonts(root)
        self.cars = CarSprites()
        self.track = None

        self.player_name = "Racer"
        self.total_score = 0
        self.total_time = 0.0
        self.race_index = 0
        self.challenge_index = 0
        self.player_progress = 0.0
        self.player_target_progress = 0.0
        self.race_start = 0
        self.question = None
        self.option_buttons = []
        self.timer_job = None
        self.answer_transition_job = None
        self.pending_finish_job = None
        self.race_active = False
        self.finished = False

        self.fuel = 100
        self.grip = 100
        self.boost = 2
        self.speed = 0
        self.penalties = 0
        self.correct = 0
        self.wrong = 0
        self.total_wrong = 0
        self.race_correct = 0
        self.race_score = 0
        self.race_penalties = 0

        self.ai = [
            {"name": "Byte", "progress": 0.0, "base": 0.76},
            {"name": "Lambda", "progress": 0.0, "base": 0.72},
            {"name": "Numpy", "progress": 0.0, "base": 0.68},
        ]
        self.history = []

        self.show_menu()

    # ---------- utility ----------
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def header(self, title, subtitle=""):
        return make_header(self.root, title, subtitle)

    def button(self, parent, text, command, width=22, bg=None, style="neutral", height=46):
        """Styled button; `width` is in pixels."""
        return RaceButton(parent, text, command, width=width, height=height, style=style)

    def restart_game(self):
        if messagebox.askyesno("Restart Game", "Restart the championship from Grand Prix 1?"):
            self.start_game()

    def quit_game(self):
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit Python Grand Prix?"):
            self.root.destroy()

    # ---------- menu ----------
    def show_menu(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.clear()

        hero = tk.Canvas(self.root, height=250, bg=S.BG, highlightthickness=0)
        hero.pack(fill="x")
        hero.bind("<Configure>", lambda e: self._safe(
            lambda: draw_hero(hero, self.cars, max(e.width, 600), 250)))

        main = tk.Frame(self.root, bg=S.BG)
        main.pack(fill="both", expand=True, pady=(18, 10))

        outer, inner = card(main, padx=40, pady=22)
        outer.pack()
        RaceButton(inner, "START CHAMPIONSHIP", self.start_game, 300, 46, "success", 12).pack(pady=6)
        RaceButton(inner, "HOW TO PLAY", self.show_instructions, 300, 46, "neutral", 12).pack(pady=6)
        RaceButton(inner, "LEADERBOARD", self.show_leaderboard, 300, 46, "neutral", 12).pack(pady=6)
        RaceButton(inner, "RESTART GAME", self.restart_game, 300, 46, "neutral", 12).pack(pady=6)
        RaceButton(inner, "QUIT GAME", self.quit_game, 300, 46, "danger", 12).pack(pady=6)

        recent = [r for r in load_scores() if r.get("type") == "race"]
        recent.sort(key=lambda r: (r.get("position", 99), -r.get("score", 0)))
        preview_outer, preview = card(main, padx=22, pady=10)
        preview_outer.pack(pady=(10, 0))
        tk.Label(preview, text="RACE LEADERBOARD  •  BEST SAVED FINISHES",
                 font=font(10, True), fg=S.ACCENT, bg=S.PANEL).pack(anchor="w")
        if recent:
            for rank, result in enumerate(recent[:3], 1):
                line = (f"{rank}. {result.get('name', 'Racer')} — {result.get('race', 'Grand Prix')} — "
                        f"P{result.get('position', '?')} — {result.get('score', 0)} pts")
                tk.Label(preview, text=line, font=font(9), fg=S.TEXT, bg=S.PANEL).pack(anchor="w", pady=1)
        else:
            tk.Label(preview, text="No race results saved yet. Complete a race to appear here.",
                     font=font(9), fg=S.MUTED, bg=S.PANEL).pack(anchor="w")
        tk.Label(main, text="5 Grand Prix  •  50 Python topics  •  3 AI rivals",
                 font=font(11, True), bg=S.BG, fg=S.YELLOW).pack(pady=(10, 0))

    def show_instructions(self):
        self.clear()
        self.header("HOW TO PLAY", "Your coding performance determines your race performance.")

        outer, body = card(self.root, padx=34, pady=22)
        outer.pack(fill="both", expand=True, padx=60, pady=14)

        lines = [
            ("1", "Choose a driver name and start the championship."),
            ("2", "Each Grand Prix asks up to 15 Python questions."),
            ("3", "Answer all 15 questions; at least 10 must be correct to cross the finish line and win."),
            ("4", "Your car advances for correct answers, then crosses the finish only after question 15 if you have at least 10 correct."),
            ("5", "You may give up to 3 wrong answers in each Grand Prix; the counter resets for the next GP."),
            ("6", "Your third wrong answer ends the current Grand Prix; you must restart it to try again."),
            ("7", "The rival cars move slowly so you have time to read and answer the quiz questions."),
            ("8", "You can unlock the next Grand Prix only after you cross the current GP finish line."),
            ("9", "If all 3 rival cars finish before you, you are placed P4 and cannot advance."),
        ]
        for n, txt in lines:
            row = tk.Frame(body, bg=S.PANEL)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=n, width=3, font=font(13, True), fg=S.TEXT, bg=S.RACE_RED,
                     pady=3).pack(side="left")
            tk.Label(row, text=txt, font=font(12), fg=S.TEXT, bg=S.PANEL,
                     anchor="w").pack(side="left", padx=16)

        self.button(self.root, "BACK", self.show_menu, 200).pack(pady=(4, 14))

    def start_game(self):
        for job_name in ("answer_transition_job", "pending_finish_job"):
            job_id = getattr(self, job_name, None)
            if job_id:
                try:
                    self.root.after_cancel(job_id)
                except tk.TclError:
                    pass
                setattr(self, job_name, None)
        name = simpledialog.askstring("Driver Registration",
                                      "Enter your driver name:",
                                      parent=self.root)
        if name and name.strip():
            self.player_name = name.strip()[:18]
        else:
            self.player_name = "Racer"

        self.total_score = 0
        self.total_time = 0
        self.race_index = 0
        self.challenge_index = 0
        self.wrong = 0
        self.race_correct = 0
        self.race_score = 0
        self.race_penalties = 0
        self.player_progress = 0.0
        self.player_target_progress = 0.0
        self.player_finish_time = None
        self.question_deck = build_question_deck(self.race_index)
        self.fuel = 100
        self.grip = 100
        self.boost = 2
        self.speed = 0
        self.penalties = 0
        self.correct = 0
        self.wrong = 0
        self.total_wrong = 0
        self.race_correct = 0
        self.race_score = 0
        self.race_penalties = 0
        self.finished = False
        self.ai = [
            {"name": "Byte", "progress": 0.0, "base": random.uniform(.70, .79)},
            {"name": "Lambda", "progress": 0.0, "base": random.uniform(.68, .76)},
            {"name": "Numpy", "progress": 0.0, "base": random.uniform(.66, .73)},
        ]
        self.history = []
        self.race_results = []
        self.race_saved = False
        self.start_race()

    # ---------- race ----------
    def start_race(self):
        self.race_active = True
        self.can_advance_to_next_gp = False
        self.challenge_index = 0
        self.wrong = 0
        self.race_correct = 0
        self.race_score = 0
        self.race_penalties = 0
        self.player_progress = 0.0
        self.player_target_progress = 0.0
        self.player_finish_time = None
        self.question_deck = build_question_deck(self.race_index)
        self.fuel = 100
        self.grip = 100
        self.boost = min(3, self.boost + 1)
        self.speed = 45
        self.race_start = time.time()
        self.race_saved = False
        self.player_finish_time = None
        # Give each rival one of three balanced pace levels, then shuffle the
        # levels so no named NPC is always the slow, medium, or fast car.
        # Approximate finish-time ranges: slow 122-133s, medium 111-120s,
        # fast 102-110s. This keeps the race competitive without rushing the quiz.
        pace_levels = [
            (0.0075, 0.0082),  # slow
            (0.0083, 0.0090),  # medium
            (0.0091, 0.0098),  # fast
        ]
        random.shuffle(pace_levels)
        npc_names = ["Byte", "Lambda", "Numpy"]
        self.ai = [
            {"name": name, "progress": 0.0,
             "pace": random.uniform(*pace_levels[index]),
             "finish_time": None}
            for index, name in enumerate(npc_names)
        ]
        self.show_race()

    def show_race(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.clear()

        race_name, start, end, desc = RACES[self.race_index]
        self.header(race_name, f"{desc}   •   Driver: {self.player_name}")
        controls = tk.Frame(self.root, bg=S.BG)
        controls.pack(fill="x", padx=25, pady=(2, 3))
        self.button(controls, "RESTART GAME", self.restart_game, 150, height=32).pack(side="right", padx=4)
        self.button(controls, "QUIT GAME", self.quit_game, 130, style="danger", height=32).pack(side="right", padx=4)
        tk.Label(controls, text=f"WRONG ANSWERS THIS GP: {self.wrong}/3",
                 font=font(9, True), fg=S.YELLOW, bg=S.BG).pack(side="left", padx=4)
        pace_text = "NPC PACE: " + "  •  ".join(
            "{} {:.2f}".format(car["name"], car["pace"]) for car in self.ai
        )
        tk.Label(controls, text=pace_text, font=font(8),
                 fg=S.MUTED, bg=S.BG).pack(side="left", padx=12)

        # top stats
        stats = tk.Frame(self.root, bg=S.BG)
        stats.pack(fill="x", padx=25, pady=(4, 4))
        self.stat_speed = self.stat(stats, "SPEED", S.ACCENT)
        self.stat_fuel = self.stat(stats, "FUEL", S.GREEN)
        self.stat_grip = self.stat(stats, "GRIP", S.YELLOW)
        self.stat_boost = self.stat(stats, "BOOST", S.PURPLE, mode="pips")
        self.stat_score = self.stat(stats, "SCORE", S.TEXT, mode="none")
        self.update_stats()

        # track
        track_frame = tk.Frame(self.root, bg=S.BORDER)
        track_frame.pack(fill="x", padx=25, pady=(4, 6))
        self.canvas = tk.Canvas(track_frame, height=S.TRACK_H, bg=S.BG, highlightthickness=0)
        self.canvas.pack(fill="x", padx=1, pady=1)
        self.track = TrackRenderer(self.canvas, self.cars)
        self.canvas.bind("<Configure>", lambda e: self.draw_track())
        self.draw_track()

        self.live_standings_label = tk.Label(
            self.root, text="", font=font(9, True), fg=S.TEXT, bg=S.BG,
            anchor="w", justify="left"
        )
        self.live_standings_label.pack(fill="x", padx=28, pady=(0, 5))
        self.update_live_standings()

        # challenge panel
        outer, self.challenge_frame = card(self.root, padx=22, pady=12)
        outer.pack(fill="both", expand=True, padx=25, pady=(0, 12))
        self.load_challenge()

        self.update_race_loop()

    def stat(self, parent, label, color, mode="bar"):
        box = StatCard(parent, label, "0", color=color, mode=mode)
        box.pack(side="left", fill="x", expand=True, padx=4)
        return box

    def draw_track(self):
        try:
            if self.track is not None and self.canvas.winfo_exists():
                self.track.draw(self.race_index, self.challenge_index, self.ai, self.player_progress)
        except tk.TclError:
            pass

    def load_challenge(self):
        for w in self.challenge_frame.winfo_children():
            w.destroy()
        self.option_buttons = []

        self.question = pick_question(self.race_index, self.challenge_index, self.question_deck)
        qtext, options, correct, explanation, key, topic_display, category = self.question
        cf = self.challenge_frame

        # bottom row first so it always stays visible: feedback + action buttons
        bottom = tk.Frame(cf, bg=S.PANEL)
        bottom.pack(side="bottom", fill="x", pady=(8, 0))
        self.feedback = tk.Label(bottom, text="Choose an answer. Correct answers trigger an automatic boost.",
                                 font=font(10, True), fg=S.TEXT, bg=S.PANEL,
                                 wraplength=900, justify="left", anchor="nw", height=3)
        self.feedback.pack(side="left", fill="x", expand=True)
        bottom.bind("<Configure>", lambda e: self._safe(
            lambda: self.feedback.config(wraplength=max(300, e.width - 30))))

        # header row: checkpoint chip, topic, progress segments
        top = tk.Frame(cf, bg=S.PANEL)
        top.pack(fill="x")
        tk.Label(top, text=f" QUESTION {self.challenge_index + 1}/15  •  CORRECT {self.race_correct}/10  •  WRONG {self.wrong}/3 ", font=font(9, True),
                 fg=S.BG, bg=S.YELLOW).pack(side="left")
        tk.Label(top, text=f"  {topic_display}  •  {category}", font=font(10, True),
                 fg=S.ACCENT, bg=S.PANEL).pack(side="left")
        seg = tk.Canvas(top, width=190, height=10, bg=S.PANEL, highlightthickness=0)
        seg.pack(side="right")
        for i in range(15):
            fill = S.GREEN if i < self.challenge_index else (S.YELLOW if i == self.challenge_index
                                                              else "#2a3244")
            x = i * (190 / 15)
            seg.create_rectangle(x, 1, x + 10, 9, fill=fill, outline="")

        # question (code-style block)
        qbox = tk.Frame(cf, bg=S.CODE_BG)
        qbox.pack(fill="x", pady=(8, 8))
        tk.Frame(qbox, bg=S.RACE_RED, width=4).pack(side="left", fill="y")
        tk.Label(qbox, text=qtext, justify="left", anchor="w", font=font(13, True, kind="mono"),
                 fg=S.TEXT, bg=S.CODE_BG, wraplength=1000, padx=14, pady=8).pack(
                     side="left", fill="x", expand=True)

        # answer options in a 2 x 2 grid
        grid = tk.Frame(cf, bg=S.PANEL)
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1, uniform="opt")
        grid.columnconfigure(1, weight=1, uniform="opt")
        for i, option in enumerate(options):
            b = OptionButton(grid, chr(65 + i), option, lambda idx=i: self.answer(idx))
            b.grid(row=i // 2, column=i % 2, sticky="ew", pady=3,
                   padx=(0, 5) if i % 2 == 0 else (5, 0))
            self.option_buttons.append(b)

    def answer(self, idx):
        """Evaluate an answer, auto-activate boost on success, and advance."""
        if not self.option_buttons or self.option_buttons[0]["state"] == "disabled":
            return

        qtext, options, correct, explanation, key, topic, category = self.question
        for button in self.option_buttons:
            button.config(state="disabled")
        self.option_buttons[correct].mark("correct")

        if idx == correct:
            self.correct += 1
            self.race_correct += 1
            self.player_target_progress = min(0.9, self.race_correct / 10.0)
            gain = 25 + max(0, 10 - self.challenge_index)
            self.total_score += gain
            self.race_score += gain
            # Correct answer automatically triggers a boost.
            self.boost = min(3, self.boost + 1)
            self.speed = min(100, self.speed + 25)
            self.fuel = min(100, self.fuel + 3)
            self.grip = min(100, self.grip + 2)
            self.total_score += 10
            self.race_score += 10
            self.feedback.config(
                text=f"✓ CORRECT! +{gain} points\n"
                     f"⚡ AUTOMATIC BOOST ACTIVATED! +25 speed, +10 bonus points\n"
                     f"{explanation}\nNext question loading...",
                fg=S.GREEN)
        else:
            self.option_buttons[idx].mark("wrong")
            self.wrong += 1
            self.total_wrong += 1
            self.race_penalties += 5
            self.penalties += 5
            self.race_score = max(0, self.race_score - 5)
            self.total_score = max(0, self.total_score - 5)
            self.speed = max(20, self.speed - 12)
            self.grip = max(0, self.grip - 8)
            if self.wrong >= 3:
                self.feedback.config(
                    text=f"✗ THIRD WRONG ANSWER!\nCorrect answer: {options[correct]}\n"
                         f"{explanation}\nYou have used all 3 allowed mistakes. This Grand Prix is over.",
                    fg=S.RED)
                self.update_stats()
                self.pending_finish_job = self.root.after(900, lambda: self.finish_race(status="third_wrong"))
                return
            self.feedback.config(
                text=f"✗ WRONG! ({self.wrong}/3 allowed) -5 points • +5 sec penalty\n"
                     f"Correct answer: {options[correct]}\n{explanation}\n"
                     f"Next question loading...",
                fg=S.RED)

        self.update_stats()
        # Briefly show feedback, then automatically move to the next question.
        self.answer_transition_job = self.root.after(350, self.next_checkpoint)

    def use_boost(self):
        """Boosts are automatic after a correct answer; no manual action is needed."""
        return

    def next_checkpoint(self):
        self.answer_transition_job = None
        # Every checkpoint consumes fuel; low fuel slows the car.
        self.fuel = max(0, self.fuel - random.randint(4, 8))
        if self.fuel < 20:
            self.speed = max(20, self.speed - 8)

        self.history.append({
            "race": self.race_index + 1,
            "question": self.challenge_index + 1,
            "topic": self.question[5],
            "correct": self.option_buttons[0]["state"] == "disabled",
        })

        self.challenge_index += 1
        if self.challenge_index >= 15:
            if self.race_correct >= 10:
                # The player reaches the finish only after answering all 15 questions
                # and earning at least 10 correct answers.
                self.player_target_progress = 1.0
                self.feedback.config(
                    text="10 correct answers achieved! Your car is heading for the finish line...",
                    fg=S.ACCENT
                )
            else:
                self.feedback.config(
                    text=f"All 15 questions completed, but you got only {self.race_correct}/10 required correct answers. Grand Prix over.",
                    fg=S.RED
                )
                self.pending_finish_job = self.root.after(
                    900, lambda: self.finish_race(status="not_enough_correct")
                )
            self.draw_track()
            self.update_stats()
        else:
            self.draw_track()
            self.load_challenge()
            self.update_stats()

    def get_race_standings(self):
        """Finished cars rank by finish time; unfinished cars follow by progress."""
        rows = [{
            "name": self.player_name, "progress": self.player_progress,
            "player": True, "finish_time": self.player_finish_time
        }]
        rows.extend({
            "name": car["name"], "progress": car["progress"],
            "player": False, "finish_time": car.get("finish_time")
        } for car in self.ai)
        finishers = [row for row in rows if row["finish_time"] is not None]
        running = [row for row in rows if row["finish_time"] is None]
        finishers.sort(key=lambda row: row["finish_time"])
        running.sort(key=lambda row: row["progress"], reverse=True)
        return finishers + running

    def update_live_standings(self):
        if not hasattr(self, "live_standings_label"):
            return
        parts = []
        for rank, row in enumerate(self.get_race_standings(), 1):
            state = (
                "FINISHED"
                if row["finish_time"] is not None
                else f"{row['progress'] * 100:.0f}%"
            )
            marker = " (YOU)" if row["player"] else ""
            parts.append(f"P{rank} {row['name']}{marker}: {state}")
        self.live_standings_label.config(text="LIVE GRAND PRIX STANDINGS   •   " + "     |     ".join(parts))

    def record_current_race(self, status):
        if self.race_saved:
            return self.current_race_position
        standings = self.get_race_standings()
        place = next(i for i, row in enumerate(standings, 1) if row["player"])
        elapsed = max(0.0, time.time() - self.race_start) + self.race_penalties
        race_name = RACES[self.race_index][0]
        save_race_result(
            self.player_name, race_name, self.race_index + 1, place,
            self.race_score, elapsed, self.race_correct, self.wrong, status
        )
        self.race_saved = True
        self.current_race_position = place
        self.race_results.append({"race": race_name, "position": place, "status": status})
        return place

    def update_stats(self):
        if hasattr(self, "stat_speed"):
            self.stat_speed.set(str(self.speed), frac=self.speed / 100)
            fuel_color = S.RED if self.fuel < 20 else (S.YELLOW if self.fuel < 40 else S.GREEN)
            self.stat_fuel.set(f"{self.fuel}%", frac=self.fuel / 100, color=fuel_color)
            self.stat_grip.set(f"{self.grip}%", frac=self.grip / 100)
            self.stat_boost.set(str(self.boost), pips=(max(0, min(3, self.boost)), 3))
            self.stat_score.set(str(self.total_score))

    def update_race_loop(self):
        if not self.race_active:
            return

        elapsed = time.time() - self.race_start
        dt = 0.08  # 80 ms animation tick

        # Player progress is earned only by correct answers.
        if self.player_progress < self.player_target_progress:
            previous = self.player_progress
            self.player_progress = min(self.player_target_progress, self.player_progress + 0.025)
            if previous < 1.0 <= self.player_progress and self.player_finish_time is None:
                self.player_finish_time = elapsed

        # Each computer driver advances at its own speed.
        for car in self.ai:
            if car["finish_time"] is not None:
                continue
            car["progress"] = min(1.0, car["progress"] + car["pace"] * dt)
            if car["progress"] >= 1.0:
                car["finish_time"] = elapsed

        if random.random() < 0.006:
            self.fuel = max(0, self.fuel - 1)
            if self.fuel == 0:
                self.speed = max(20, self.speed - 10)

        self.update_stats()
        self.draw_track()
        self.update_live_standings()

        # Finish as soon as the player crosses, or when all 3 NPCs finish first.
        if self.player_finish_time is not None:
            self.finish_race(status="finished")
            return
        if all(car["finish_time"] is not None for car in self.ai):
            self.finish_race(status="all_npc_finished")
            return

        self.timer_job = self.root.after(80, self.update_race_loop)

    def finish_race(self, status="finished"):
        if not self.race_active:
            return
        for job_name in ("answer_transition_job", "pending_finish_job"):
            job_id = getattr(self, job_name, None)
            if job_id:
                try:
                    self.root.after_cancel(job_id)
                except tk.TclError:
                    pass
                setattr(self, job_name, None)
        self.race_active = False
        self.can_advance_to_next_gp = (status == "finished" and self.player_finish_time is not None)
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        elapsed = time.time() - self.race_start + self.race_penalties
        self.total_time += elapsed

        # Record the actual track order; the player's position is not automatically P1.
        place = self.record_current_race(status)
        standings = self.get_race_standings()

        if self.race_index >= 4:        # last race: straight to the championship screen
            self.finish_championship()
            return

        self.clear()
        race_name = RACES[self.race_index][0]
        self.header(f"{race_name} FINISHED", "Final positions are based on finish-line crossing order.")

        outer, inner = card(self.root, padx=35, pady=22)
        outer.pack(fill="x", padx=80, pady=18)

        banner = tk.Canvas(inner, width=440, height=64, bg=S.PANEL, highlightthickness=0)
        banner.pack()
        ui.draw_flag(banner, 40, 8, size=32)
        banner.create_text(96, 32, text="RACE COMPLETE", anchor="w", fill=S.GREEN,
                           font=font(24, True, True, "display"))

        tk.Label(inner, text="FINAL STANDINGS", font=font(10, True),
                 fg=S.ACCENT, bg=S.PANEL).pack(pady=(6, 2))
        for rank, item in enumerate(standings, 1):
            suffix = "  ← YOU" if item["player"] else ""
            state = "FINISHED" if item["finish_time"] is not None else f"{item['progress'] * 100:.0f}%"
            tk.Label(inner, text=f"P{rank}  {item['name']}{suffix}  •  {state}",
                     font=font(10, rank == place),
                     fg=S.YELLOW if item["player"] else S.MUTED, bg=S.PANEL).pack()

        tiles = tk.Frame(inner, bg=S.PANEL)
        tiles.pack(fill="x", pady=(10, 4))
        for label, value, color in (("RACE TIME", f"{elapsed:.1f} s", S.TEXT),
                                    ("CORRECT", str(self.race_correct), S.GREEN),
                                    ("WRONG", str(self.wrong), S.RED),
                                    ("GP SCORE", str(self.race_score), S.YELLOW)):
            self._tile(tiles, label, value, color)

        note = ("All 3 rival cars crossed the finish line first. You are placed P4."
                if status == "all_npc_finished" else
                "This Grand Prix ended after your third wrong answer."
                if status == "third_wrong" else
                "You answered all 15 questions but did not reach the 10 correct answers required to finish."
                if status == "not_enough_correct" else
                "Position is based on the order cars crossed the finish line.")
        tk.Label(inner, text=note, font=font(9, True), fg=S.MUTED, bg=S.PANEL).pack(pady=(8, 0))
        tk.Label(inner, text=f"Race position: P{place}", font=font(19, True, True, "display"),
                 fg=S.ACCENT, bg=S.PANEL).pack(pady=(12, 0))

        result_buttons = tk.Frame(self.root, bg=S.BG)
        result_buttons.pack(pady=8)
        if self.can_advance_to_next_gp:
            self.button(result_buttons, "NEXT GRAND PRIX", self.next_race, 220, style="accent").pack(side="left", padx=5)
        else:
            tk.Label(
                result_buttons,
                text="Grand Prix not completed. Finish the race to unlock the next Grand Prix.",
                font=font(9, True), fg=S.YELLOW, bg=S.BG
            ).pack(side="left", padx=8)
        self.button(result_buttons, "RESTART CHAMPIONSHIP", self.restart_game, 210).pack(side="left", padx=5)
        self.button(result_buttons, "QUIT GAME", self.quit_game, 140, style="danger").pack(side="left", padx=5)

    def _tile(self, parent, label, value, color):
        t = tk.Frame(parent, bg=S.PANEL2, highlightbackground=S.BORDER, highlightthickness=1)
        t.pack(side="left", fill="x", expand=True, padx=5)
        tk.Frame(t, bg=color, height=3).pack(fill="x")
        tk.Label(t, text=label, font=font(8, True), fg=S.MUTED, bg=S.PANEL2).pack(pady=(8, 0))
        tk.Label(t, text=value, font=font(17, True, kind="display"), fg=color,
                 bg=S.PANEL2).pack(pady=(0, 10))

    def next_race(self):
        if not getattr(self, "can_advance_to_next_gp", False):
            messagebox.showwarning(
                "Grand Prix Locked",
                "Complete the current Grand Prix and cross the finish line before advancing."
            )
            return
        self.can_advance_to_next_gp = False
        self.race_index += 1
        self.start_race()

    # ---------- championship ----------
    def finish_championship(self):
        self.finished = True
        self.save_result()
        self.clear()
        self.header("CHAMPIONSHIP COMPLETE", "Final championship standings are ranked by total score.")

        outer, inner = card(self.root, padx=28, pady=16)
        outer.pack(fill="both", expand=True, padx=45, pady=(8, 6))
        tk.Label(inner, text="★  CHAMPIONSHIP RESULTS  ★",
                 font=font(21, True, True, "display"), fg=S.YELLOW, bg=S.PANEL).pack(pady=(0, 3))
        tk.Label(inner, text=self.player_name, font=font(17, True, kind="display"),
                 fg=S.ACCENT, bg=S.PANEL).pack(pady=(0, 5))

        for label, value, color in (
            ("YOUR FINAL SCORE", str(self.total_score), S.YELLOW),
            ("TOTAL RACE TIME", f"{self.total_time:.1f} s", S.TEXT),
            ("CORRECT", str(self.correct), S.GREEN),
            ("TOTAL WRONG", str(self.total_wrong), S.RED),
        ):
            self._tile(inner, label, value, color)

        records = [r for r in load_scores() if r.get("type") != "race"]
        records.sort(key=lambda r: (-r.get("score", 0), r.get("time", 0)))
        tk.Label(inner, text="FINAL CHAMPIONSHIP STANDINGS  •  RANKED BY SCORE",
                 font=font(10, True), fg=S.ACCENT, bg=S.PANEL).pack(pady=(10, 3))
        table = tk.Frame(inner, bg=S.PANEL)
        table.pack(fill="x")
        headers = ["RANK", "DRIVER", "TOTAL SCORE", "TIME"]
        widths = [8, 22, 14, 14]
        for col, heading in enumerate(headers):
            tk.Label(table, text=heading, width=widths[col], anchor="w",
                     font=font(9, True), fg=S.YELLOW, bg=S.PANEL).grid(row=0, column=col, padx=4)
        current_rank = None
        for rank, rec in enumerate(records[:8], 1):
            is_current = (
                rec.get("name") == self.player_name
                and rec.get("score") == self.total_score
                and rec.get("time") == round(self.total_time, 1)
            )
            if is_current and current_rank is None:
                current_rank = rank
            vals = [rank, rec.get("name", "Racer"), rec.get("score", 0),
                    f"{rec.get('time', 0):.1f}s"]
            for col, value in enumerate(vals):
                tk.Label(table, text=str(value), width=widths[col], anchor="w",
                         font=font(9, is_current or rank <= 3),
                         fg=S.GREEN if is_current else S.TEXT,
                         bg=S.PANEL2 if rank % 2 == 0 else S.PANEL).grid(
                             row=rank, column=col, padx=4, pady=2)
        if current_rank is None:
            current_rank = next((i for i, rec in enumerate(records, 1)
                                 if rec.get("name") == self.player_name
                                 and rec.get("score") == self.total_score), None)
        tk.Label(inner, text=f"YOUR CHAMPIONSHIP RANK: P{current_rank or '50+'}",
                 font=font(13, True), fg=S.GREEN, bg=S.PANEL).pack(pady=(7, 0))

        row = tk.Frame(self.root, bg=S.BG)
        row.pack(pady=7)
        self.button(row, "LEADERBOARD", self.show_leaderboard, 190).pack(side="left", padx=5)
        self.button(row, "RESTART GAME", self.restart_game, 190, style="success").pack(side="left", padx=5)
        self.button(row, "QUIT GAME", self.quit_game, 150, style="danger").pack(side="left", padx=5)

    def save_result(self):
        save_result(self.player_name, self.total_score, self.total_time, self.correct, self.total_wrong,
                    [item['position'] for item in self.race_results])

    def show_leaderboard(self):
        self.clear()
        self.header("LEADERBOARD", "Saved race finishes and championship results on this computer.")
        records = load_scores()
        race_records = [r for r in records if r.get("type") == "race"]
        champ_records = [r for r in records if r.get("type") != "race"]
        race_records.sort(key=lambda r: (r.get("position", 99), -r.get("score", 0), r.get("time", 0)))
        champ_records.sort(key=lambda r: (-r.get("score", 0), r.get("time", 0)))

        outer, panel = card(self.root, padx=16, pady=10)
        outer.pack(fill="both", expand=True, padx=28, pady=8)

        tk.Label(panel, text="RACE-BY-RACE HISTORY", font=font(11, True),
                 fg=S.ACCENT, bg=S.PANEL).pack(anchor="w", pady=(0, 4))
        race_table = tk.Frame(panel, bg=S.PANEL)
        race_table.pack(fill="x", pady=(0, 10))
        race_headers = ["#", "DRIVER", "GRAND PRIX", "PLACE", "SCORE", "STATUS", "DATE"]
        race_widths = [3, 14, 16, 6, 7, 11, 16]
        for col, label in enumerate(race_headers):
            tk.Label(race_table, text=label, width=race_widths[col], anchor="w",
                     font=font(8, True), fg=S.YELLOW, bg=S.PANEL).grid(row=0, column=col, padx=1)
        for row_num, rec in enumerate(reversed(race_records[-10:]), 1):
            vals = [row_num, rec.get("name", "Racer"), rec.get("race", "Grand Prix"),
                    f"P{rec.get('position', '?')}", rec.get("score", 0),
                    rec.get("status", "finished").upper(), rec.get("date", "")]
            for col, value in enumerate(vals):
                bg = S.PANEL if row_num % 2 else S.PANEL2
                tk.Label(race_table, text=str(value), width=race_widths[col], anchor="w",
                         font=font(8), fg=S.TEXT, bg=bg).grid(row=row_num, column=col, padx=1, pady=2)
        if not race_records:
            tk.Label(race_table, text="No race results saved yet.",
                     font=font(9), fg=S.MUTED, bg=S.PANEL).grid(row=1, column=0, columnspan=7)

        tk.Label(panel, text="CHAMPIONSHIP RANKINGS", font=font(11, True),
                 fg=S.ACCENT, bg=S.PANEL).pack(anchor="w", pady=(5, 4))
        champ_table = tk.Frame(panel, bg=S.PANEL)
        champ_table.pack(fill="x")
        champ_headers = ["#", "DRIVER", "SCORE", "TIME", "CORRECT", "WRONG", "DATE"]
        champ_widths = [3, 16, 8, 9, 8, 7, 16]
        for col, label in enumerate(champ_headers):
            tk.Label(champ_table, text=label, width=champ_widths[col], anchor="w",
                     font=font(8, True), fg=S.YELLOW, bg=S.PANEL).grid(row=0, column=col, padx=1)
        for row_num, rec in enumerate(champ_records[:8], 1):
            vals = [row_num, rec.get("name", "Racer"), rec.get("score", 0),
                    f"{rec.get('time', 0):.1f}s", rec.get("correct", 0),
                    rec.get("wrong", 0), rec.get("date", "")]
            for col, value in enumerate(vals):
                bg = S.PANEL if row_num % 2 else S.PANEL2
                tk.Label(champ_table, text=str(value), width=champ_widths[col], anchor="w",
                         font=font(8), fg=S.TEXT, bg=bg).grid(row=row_num, column=col, padx=1, pady=2)
        if not champ_records:
            tk.Label(champ_table, text="No completed championship yet.",
                     font=font(9), fg=S.MUTED, bg=S.PANEL).grid(row=1, column=0, columnspan=7)

        self.button(self.root, "BACK TO MENU", self.show_menu, 220).pack(pady=(2, 8))

    # ---------- helpers ----------
    @staticmethod
    def _safe(fn):
        try:
            fn()
        except tk.TclError:
            pass
