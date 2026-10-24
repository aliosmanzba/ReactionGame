import json
import math
import os
import pygame
import random
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


class ReactionGame:
    MIN_GREEN_DURATION_MS = 100
    MAX_GREEN_DURATION_MS = 400
    FLY_HITBOX_PADDING = 22
    COLORS = {
        "background": "#10131C",
        "panel": "#191E2B",
        "muted": "#929AAF",
        "text": "#F4F6FB",
        "red": "#F05252",
        "green": "#37D996",
        "neutral": "#343B4D",
        "button": "#6875F5",
        "button_active": "#7B86FF",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Reaction Game")
        self.root.geometry("1525x830")
        self.root.resizable(True, True)
        self.root.configure(bg=self.COLORS["background"])
        self.root.attributes("-fullscreen", True)
        self.sound_dir = Path(__file__).resolve().parent / "Sounds"
        pygame.mixer.init()
        pygame.mixer.music.load(str(self.sound_dir / "lofi.ogg"))
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)
        self.hit_sound = pygame.mixer.Sound(str(self.sound_dir / "hit.wav"))
        self.miss_sound = pygame.mixer.Sound(str(self.sound_dir / "miss.wav"))

        self.hit_sound.set_volume(0.7)
        self.miss_sound.set_volume(0.7)
        self.background_canvas = tk.Canvas(
            root,
            bg="#3E2723",
            highlightthickness=0,
            cursor="none",
        )
        self.background_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        wood = random.Random(12)
        grain_colors = ("#5D4037", "#6D4C41", "#795548", "#8D6E63")
        grain_spacing = 24

        for y in range(18, screen_height, grain_spacing):
            points = []
            offset = wood.randint(-10, 10)

            for x in range(0, screen_width + 41, 40):
                points.extend((x, y + offset + wood.randint(-5, 5)))

            self.background_canvas.create_line(
                *points,
                fill=wood.choice(grain_colors),
                width=wood.choice((1, 1, 2)),
                smooth=True,
            )

        for _ in range(42):
            base_y = wood.randrange(18, screen_height, grain_spacing)
            start_x = wood.randint(0, screen_width)
            length = wood.randint(35, 150)
            branch_points = [
                start_x,
                base_y,
                start_x + length // 3,
                base_y + wood.randint(-10, 10),
                start_x + length * 2 // 3,
                base_y + wood.randint(-18, 18),
                start_x + length,
                base_y + wood.randint(-12, 12),
            ]
            self.background_canvas.create_line(
                *branch_points,
                fill=wood.choice(grain_colors),
                width=1,
                smooth=True,
            )

        for _ in range(5):
            center_x = wood.randint(100, max(100, screen_width - 100))
            center_y = wood.randint(80, max(80, screen_height - 80))
            radius_x = wood.randint(24, 48)
            radius_y = wood.randint(12, 25)
            phase = wood.random() * math.tau

            for ring in range(4):
                points = []
                ring_x = radius_x + ring * 7
                ring_y = radius_y + ring * 4

                for step in range(49):
                    angle = math.tau * step / 48
                    wobble = math.sin(angle * 3 + phase) * 2
                    x = center_x + (ring_x + wobble) * math.cos(angle)
                    y = center_y + (ring_y + wobble) * math.sin(angle)
                    points.extend((x, y))

                self.background_canvas.create_line(
                    *points,
                    fill=grain_colors[(ring + 1) % len(grain_colors)],
                    width=1,
                    smooth=True,
                )

        plate_center_x = screen_width // 2
        plate_center_y = screen_height // 2
        self.background_canvas.create_oval(
            plate_center_x - 297,
            plate_center_y - 152,
            plate_center_x + 297,
            plate_center_y + 152,
            fill="#241714",
            outline="",
        )
        self.background_canvas.create_oval(
            plate_center_x - 284,
            plate_center_y - 169,
            plate_center_x + 284,
            plate_center_y + 133,
            fill="#E8E0D2",
            outline="#B8AA98",
            width=6,
        )
        self.background_canvas.create_oval(
            plate_center_x - 224,
            plate_center_y - 135,
            plate_center_x + 224,
            plate_center_y + 99,
            fill="#F6F0E5",
            outline="#D1C5B5",
            width=5,
        )
        self.background_canvas.create_oval(
            plate_center_x - 191,
            plate_center_y - 115,
            plate_center_x + 191,
            plate_center_y + 85,
            fill="#D9A85F",
            outline="#B7803D",
            width=4,
        )
        for food_x, food_y, food_size in (
            (-85, -35, 25),
            (53, -60, 20),
            (-15, 32, 29),
            (102, 15, 17),
        ):
            self.background_canvas.create_oval(
                plate_center_x + food_x - food_size,
                plate_center_y + food_y - food_size,
                plate_center_x + food_x + food_size,
                plate_center_y + food_y + food_size,
                fill="#8C3F24",
                outline="",
            )

        self.fly_random = random.Random()
        self.fly_x = screen_width * 0.25
        self.fly_y = screen_height * 0.3
        self.fly_target = None
        self.fly_is_landing = False
        self.fly_hidden = False
        self.fly_animation_after = None
        self.background_canvas.create_oval(
            self.fly_x - 15,
            self.fly_y - 9,
            self.fly_x + 21,
            self.fly_y + 12,
            fill="#171311",
            outline="",
            tags=("fly",),
        )
        self.background_canvas.create_oval(
            self.fly_x - 15,
            self.fly_y - 30,
            self.fly_x + 3,
            self.fly_y - 6,
            fill="#B7C7C7",
            outline="#303A3B",
            tags=("fly",),
        )
        self.background_canvas.create_oval(
            self.fly_x + 3,
            self.fly_y - 32,
            self.fly_x + 21,
            self.fly_y - 8,
            fill="#B7C7C7",
            outline="#303A3B",
            tags=("fly",),
        )
        self.background_canvas.create_oval(
            self.fly_x + 18,
            self.fly_y - 6,
            self.fly_x + 30,
            self.fly_y + 6,
            fill="#241D19",
            outline="",
            tags=("fly",),
        )
        self.fly_items = "fly"
        self.fly_food_center = (plate_center_x, plate_center_y)
        self.fly_screen_size = (screen_width, screen_height)
        self._schedule_fly_animation(700)

        self.background_canvas.create_text(
            screen_width // 2,
            55,
            text="Reaction Game",
            fill="#F4F6FB",
            font=("Arial", 18, "bold"),
        )
        self.background_canvas.create_text(
            screen_width // 2,
            92,
            text="Wait for the fly to approach the food",
            fill="#E6D4C5",
            font=("Arial", 12),
        )
        self.hand_x = 0
        self.hand_y = 0
        self.hand_cursor_initialized = False
        hand_skin = "#F0C9A5"
        hand_outline = "#38271F"
        self.background_canvas.create_polygon(
            12, 48, 8, 39, 4, 32, 6, 27, 11, 27,
            15, 34, 13, 12, 15, 7, 20, 8, 22, 32,
            22, 6, 25, 2, 30, 4, 30, 33, 32, 12,
            35, 8, 40, 10, 39, 36, 42, 21, 46, 18,
            50, 21, 48, 40, 42, 52, 23, 57,
            fill=hand_skin,
            outline=hand_outline,
            width=2,
            smooth=True,
            tags=("hand_cursor", "hand_open"),
        )
        self.background_canvas.create_polygon(
            9, 28, 14, 19, 21, 17, 28, 18, 37, 20,
            44, 26, 42, 40, 36, 49, 19, 49, 10, 41,
            fill=hand_skin,
            outline=hand_outline,
            width=2,
            smooth=True,
            state="hidden",
            tags=("hand_cursor", "hand_closed"),
        )
        self.background_canvas.create_line(
            21, 23, 39, 25,
            fill=hand_outline,
            width=2,
            state="hidden",
            tags=("hand_cursor", "hand_closed"),
        )
        self.background_canvas.create_line(
            19, 30, 40, 32,
            fill=hand_outline,
            width=2,
            state="hidden",
            tags=("hand_cursor", "hand_closed"),
        )
        self.background_canvas.create_line(
            18, 37, 39, 39,
            fill=hand_outline,
            width=2,
            state="hidden",
            tags=("hand_cursor", "hand_closed"),
        )
        self.background_canvas.bind("<Motion>", self._move_hand_cursor)
        self.background_canvas.bind("<ButtonPress-1>", self._press_hand_cursor)
        self.background_canvas.bind("<ButtonRelease-1>", self._release_hand_cursor)

        self.root.bind("<Escape>", self.exit_fullscreen)
        self.score_panel = self.background_canvas
        self.score_origin_x = int(screen_width * 0.02)
        self.score_origin_y = int(screen_height * 0.5 - 150)

        self.score_panel.create_text(
            130,
            52,
            text="TOP 5",
            fill=self.COLORS["text"],
            font=("Arial", 16, "bold"),
            tags=("score_panel", "score_table_frame"),
        )

        table_left, table_top = 30, 34
        table_right, table_bottom = 250, 274
        title_bottom = 70
        header_bottom = 104
        column_divider = 83
        grid_color = "#E8DFD5"

        self.score_panel.create_rectangle(
            table_left,
            table_top,
            table_right,
            table_bottom,
            outline=grid_color,
            width=2,
            tags=("score_panel", "score_table_frame"),
        )
        self.score_panel.create_line(
            table_left,
            title_bottom,
            table_right,
            title_bottom,
            fill=grid_color,
            width=2,
            tags=("score_panel", "score_table_frame"),
        )
        self.score_panel.create_line(
            table_left,
            header_bottom,
            table_right,
            header_bottom,
            fill=grid_color,
            width=2,
            tags=("score_panel", "score_table_frame"),
        )
        self.score_panel.create_line(
            column_divider,
            title_bottom,
            column_divider,
            table_bottom,
            fill=grid_color,
            width=1,
            tags=("score_panel", "score_table_frame"),
        )

        for row in range(1, 5):
            y = header_bottom + row * 34
            self.score_panel.create_line(
                table_left,
                y,
                table_right,
                y,
                fill=grid_color,
                width=1,
                tags=("score_panel", "score_table_frame"),
            )

        self.score_panel.create_text(
            (table_left + column_divider) / 2,
            (title_bottom + header_bottom) / 2,
            text="#",
            fill=self.COLORS["text"],
            font=("Arial", 10, "bold"),
            tags=("score_panel", "score_table_frame"),
        )
        self.score_panel.create_text(
            (column_divider + table_right) / 2,
            (title_bottom + header_bottom) / 2,
            text="Time (ms)",
            fill=self.COLORS["text"],
            font=("Arial", 10, "bold"),
            tags=("score_panel", "score_table_frame"),
        )
        self.score_panel.move(
            "score_panel",
            self.score_origin_x,
            self.score_origin_y,
        )
        self.score_panel.tag_raise("score_panel")
        self.score_panel.tag_raise("hand_cursor")

        self.rules_origin_x = screen_width - self.score_origin_x - 280
        self.rules_origin_y = self.score_origin_y
        rules_tag = ("rules_panel", "rules_table_frame")
        self.score_panel.create_text(
            self.rules_origin_x + 130,
            self.rules_origin_y + 52,
            text="HOW TO PLAY",
            fill=self.COLORS["text"],
            font=("Arial", 14, "bold"),
            tags=rules_tag,
        )

        rules_left, rules_top = 30, 34
        rules_right, rules_bottom = 250, 274
        rules_title_bottom = 70
        rules_divider = 62
        self.score_panel.create_rectangle(
            self.rules_origin_x + rules_left,
            self.rules_origin_y + rules_top,
            self.rules_origin_x + rules_right,
            self.rules_origin_y + rules_bottom,
            outline=grid_color,
            width=2,
            tags=rules_tag,
        )
        self.score_panel.create_line(
            self.rules_origin_x + rules_left,
            self.rules_origin_y + rules_title_bottom,
            self.rules_origin_x + rules_right,
            self.rules_origin_y + rules_title_bottom,
            fill=grid_color,
            width=2,
            tags=rules_tag,
        )
        self.score_panel.create_line(
            self.rules_origin_x + rules_divider,
            self.rules_origin_y + rules_title_bottom,
            self.rules_origin_x + rules_divider,
            self.rules_origin_y + rules_bottom,
            fill=grid_color,
            width=1,
            tags=rules_tag,
        )

        rules = (
            "Wait for the fly to land on the food.",
            "The fly can only be hit while it is on the food.",
            "Click the fly quickly — it stays for only 0.1–0.4 seconds.",
            "Your reaction time starts when the fly lands. Faster hits earn better scores.",
        )
        rules_row_height = (rules_bottom - rules_title_bottom) / len(rules)
        for index, rule in enumerate(rules):
            row_top = rules_title_bottom + index * rules_row_height
            row_center = row_top + rules_row_height / 2
            if index:
                self.score_panel.create_line(
                    self.rules_origin_x + rules_left,
                    self.rules_origin_y + row_top,
                    self.rules_origin_x + rules_right,
                    self.rules_origin_y + row_top,
                    fill=grid_color,
                    width=1,
                    tags=rules_tag,
                )
            self.score_panel.create_text(
                self.rules_origin_x + (rules_left + rules_divider) / 2,
                self.rules_origin_y + row_center,
                text=str(index + 1),
                fill=self.COLORS["text"],
                font=("Arial", 10, "bold"),
                tags=rules_tag,
            )
            self.score_panel.create_text(
                self.rules_origin_x + rules_divider + 8,
                self.rules_origin_y + row_center,
                text=rule,
                width=rules_right - rules_divider - 16,
                anchor="w",
                justify="left",
                fill=self.COLORS["text"],
                font=("Arial", 9),
                tags=rules_tag,
            )
        self.score_panel.tag_raise("rules_panel")
        self.score_panel.tag_raise("hand_cursor")

        self.state = "idle"
        self.green_timer = None
        self.landing_started_at = None
        local_app_data = Path(
            os.environ.get(
                "LOCALAPPDATA",
                str(Path.home() / "AppData" / "Local"),
            )
        )
        self.scores_file = local_app_data / "ReactionGame" / "scores.json"
        self.best_scores = self._load_scores()
        self._refresh_score_table()

    def _choose_fly_destination(self):
        screen_width, screen_height = self.fly_screen_size
        self.fly_is_landing = self.state == "flying" and self.fly_random.random() < 0.3
        if self.fly_is_landing:
            food_x, food_y = self.fly_food_center
            target_x = food_x + self.fly_random.randint(-108, 108)
            target_y = food_y + self.fly_random.randint(-54, 54)
        elif self.fly_random.random() < 0.7:
            food_x, food_y = self.fly_food_center
            target_x = food_x + self.fly_random.randint(-160, 160)
            target_y = food_y + self.fly_random.randint(-83, 83)
        else:
            target_x = self.fly_random.randint(20, screen_width - 20)
            target_y = self.fly_random.randint(130, screen_height - 20)

        self.fly_target = (
            max(12, min(screen_width - 12, target_x)),
            max(115, min(screen_height - 12, target_y)),
        )

    def _schedule_fly_animation(self, delay_ms):
        if self.fly_animation_after is None:
            self.fly_animation_after = self.root.after(
                delay_ms,
                self._run_fly_animation,
            )

    def _run_fly_animation(self):
        self.fly_animation_after = None
        self._animate_fly()

    def _move_hand_cursor(self, event):
        if self.hand_cursor_initialized:
            move_x = event.x - self.hand_x
            move_y = event.y - self.hand_y
        else:
            move_x = event.x - 27
            move_y = event.y - 3
            self.hand_cursor_initialized = True

        self.background_canvas.move("hand_cursor", move_x, move_y)
        self.background_canvas.tag_raise("hand_cursor")
        self.hand_x = event.x
        self.hand_y = event.y

    def _press_hand_cursor(self, event):
        self.background_canvas.itemconfigure("hand_open", state="hidden")
        self.background_canvas.itemconfigure("hand_closed", state="normal")
        self.on_target_click(event)
        return "break"

    def _release_hand_cursor(self, _event):
        self.background_canvas.itemconfigure("hand_closed", state="hidden")
        self.background_canvas.itemconfigure("hand_open", state="normal")

    def _animate_fly(self):
        if self.fly_hidden:
            return

        if self.fly_target is None:
            self._choose_fly_destination()

        target_x, target_y = self.fly_target
        dx = target_x - self.fly_x
        dy = target_y - self.fly_y
        distance = math.hypot(dx, dy)

        if distance < 7:
            if distance:
                self.background_canvas.move(self.fly_items, dx, dy)
                self.fly_x = target_x
                self.fly_y = target_y

            if self.fly_is_landing and self.state == "flying":
                self.fly_is_landing = False
                self.state = "green"
                self.landing_started_at = time.perf_counter()
                green_duration_ms = self.fly_random.randint(
                    self.MIN_GREEN_DURATION_MS,
                    self.MAX_GREEN_DURATION_MS,
                )
                self.green_timer = self.root.after(
                    green_duration_ms,
                    self.green_time_expired,
                )
                return

            self.fly_target = None
            pause_ms = self.fly_random.randint(250, 700)
            self._schedule_fly_animation(pause_ms)
            return

        step = min(4.58, distance)
        move_x = dx / distance * step
        move_y = dy / distance * step
        self.background_canvas.move(self.fly_items, move_x, move_y)
        self.fly_x += move_x
        self.fly_y += move_y
        self._schedule_fly_animation(30)

    def exit_fullscreen(self, _event=None):
        self.root.attributes("-fullscreen", False)

    def start_round(self):
        self.cancel_timers()
        self.state = "flying"
        self.fly_is_landing = False
        self.landing_started_at = None
        self.fly_target = None
        self._schedule_fly_animation(0)

    def on_target_click(self, event=None):
        if self.state == "idle" or self.state in ("won", "lost", "missed"):
            self.start_round()
        elif self.state == "green" and event is not None:
            if self._is_fly_hit(event.x, event.y):
                self._register_hit()
            else:
                self.miss_sound.play()

    def _is_fly_hit(self, x, y):
        bounds = self.background_canvas.bbox(self.fly_items)
        if bounds is None:
            return False

        left, top, right, bottom = bounds
        padding = self.FLY_HITBOX_PADDING
        return (
            left - padding <= x <= right + padding
            and top - padding <= y <= bottom + padding
        )

    def _register_hit(self):
        if self.state != "green" or self.landing_started_at is None:
            return

        self.hit_sound.play()
        reaction_ms = (time.perf_counter() - self.landing_started_at) * 1000
        self.best_scores.append(reaction_ms)
        self.best_scores.sort()
        del self.best_scores[5:]
        self._save_scores()
        self._refresh_score_table()
        self._show_hit_effect()
        self.finish_round("won")

    def _load_scores(self):
        try:
            with self.scores_file.open("r", encoding="utf-8") as scores_file:
                scores = json.load(scores_file)
        except FileNotFoundError:
            return []
        except (OSError, json.JSONDecodeError) as error:
            messagebox.showwarning(
                "Skorlar yüklenemedi",
                f"Skor dosyası okunamadı:\n{error}",
                parent=self.root,
            )
            return []

        if not isinstance(scores, list) or any(
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(score)
            or score < 0
            for score in scores
        ):
            messagebox.showwarning(
                "Skor dosyası geçersiz",
                "Skor dosyasının biçimi geçersiz. Yeni skorlar bu dosyaya kaydedilecek.",
                parent=self.root,
            )
            return []

        return sorted(scores)[:5]

    def _save_scores(self):
        try:
            self.scores_file.parent.mkdir(parents=True, exist_ok=True)
            with self.scores_file.open("w", encoding="utf-8") as scores_file:
                json.dump(self.best_scores, scores_file, indent=2)
        except OSError as error:
            messagebox.showerror(
                "Skorlar kaydedilemedi",
                f"Skor dosyasına yazılamadı:\n{error}",
                parent=self.root,
            )

    def _refresh_score_table(self):
        if not hasattr(self, "score_panel"):
            return

        self.score_panel.delete("score_table_values")
        for rank in range(1, 6):
            if rank <= len(self.best_scores):
                value = f"{self.best_scores[rank - 1]:.1f}"
            else:
                value = "--"
            y = self.score_origin_y + 121 + (rank - 1) * 34
            self.score_panel.create_text(
                self.score_origin_x + 56,
                y,
                text=str(rank),
                fill=self.COLORS["text"],
                font=("Arial", 11),
                tags=("score_panel", "score_table_values"),
            )
            self.score_panel.create_text(
                self.score_origin_x + 166,
                y,
                text=value,
                fill=self.COLORS["text"],
                font=("Arial", 11),
                tags=("score_panel", "score_table_values"),
            )
        self.score_panel.tag_raise("score_panel")
        self.score_panel.tag_raise("hand_cursor")

    def green_time_expired(self):
        self.green_timer = None
        if self.state == "green":
            self.finish_round("missed")

    def finish_round(self, state):
        self.cancel_timers()
        self.state = state
        self.fly_is_landing = False
        self.landing_started_at = None
        self.fly_target = None
        self._schedule_fly_animation(150)

    def _show_hit_effect(self):
        self.fly_hidden = True
        self.background_canvas.itemconfigure("fly", state="hidden")
        burst_items = []
        burst_colors = ("#FFE082", "#FFB74D", "#FFF3E0")

        for index in range(10):
            angle = math.tau * index / 10
            end_x = self.fly_x + math.cos(angle) * 12
            end_y = self.fly_y + math.sin(angle) * 12
            burst_items.append(
                self.background_canvas.create_line(
                    self.fly_x,
                    self.fly_y,
                    end_x,
                    end_y,
                    fill=burst_colors[index % len(burst_colors)],
                    width=4,
                    capstyle=tk.ROUND,
                    tags=("hit_effect",),
                )
            )
            burst_items.append(
                self.background_canvas.create_oval(
                    self.fly_x - 3,
                    self.fly_y - 3,
                    self.fly_x + 3,
                    self.fly_y + 3,
                    fill=burst_colors[index % len(burst_colors)],
                    outline="",
                    tags=("hit_effect",),
                )
            )

        self._animate_hit_effect(burst_items, 0)

    def _animate_hit_effect(self, items, frame):
        if frame >= 4:
            self.background_canvas.delete("hit_effect")
            self.background_canvas.itemconfigure("fly", state="normal")
            self.fly_hidden = False
            self._schedule_fly_animation(150)
            return

        radius = 12 + frame * 11
        for index in range(10):
            angle = math.tau * index / 10
            line_id = items[index * 2]
            dot_id = items[index * 2 + 1]
            end_x = self.fly_x + math.cos(angle) * radius
            end_y = self.fly_y + math.sin(angle) * radius
            self.background_canvas.coords(
                line_id,
                self.fly_x,
                self.fly_y,
                end_x,
                end_y,
            )
            dot_x = self.fly_x + math.cos(angle) * radius
            dot_y = self.fly_y + math.sin(angle) * radius
            self.background_canvas.coords(
                dot_id,
                dot_x - 3,
                dot_y - 3,
                dot_x + 3,
                dot_y + 3,
            )

        self.root.after(60, self._animate_hit_effect, items, frame + 1)

    def cancel_timers(self):
        if self.green_timer is not None:
            self.root.after_cancel(self.green_timer)
            self.green_timer = None


if __name__ == "__main__":
    window = tk.Tk()
    game = ReactionGame(window)
    window.mainloop()
