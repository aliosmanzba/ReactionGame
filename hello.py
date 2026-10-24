import random
import tkinter as tk


class ReactionGame:
    MIN_GREEN_DURATION_MS = 100
    MAX_GREEN_DURATION_MS = 400
    MIN_WAIT_SECONDS = 2
    MAX_WAIT_SECONDS = 5
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
        self.root.title("Raction Game")
        self.root.geometry("1525x830")
        self.root.resizable(True, True)
        self.root.configure(bg=self.COLORS["background"])
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.state = "idle"
        self.green_timer = None
        self.wait_timer = None

        self.content = tk.Frame(root, bg=self.COLORS["background"])
        self.content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.content,
            text="Reaction Game",
            font=("Arial", 11, "bold"),
            fg=self.COLORS["button_active"],
            bg=self.COLORS["background"],
        ).pack(pady=(28, 5))

        tk.Label(
            self.content,
            text="How fast you are?",
            font=("Arial", 24, "bold"),
            fg=self.COLORS["text"],
            bg=self.COLORS["background"],
        ).pack()

        tk.Label(
            self.content,
            text=("Wait on red. Click as soon as you see green!"),
            font=("Arial", 11),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
        ).pack(pady=(7, 20))

        self.panel = tk.Frame(
            self.content,
            bg=self.COLORS["panel"],
            padx=24,
            pady=18,
            width=430,
            height=400,
        )
        self.panel.pack(padx=32)
        self.panel.pack_propagate(False)

        self.message = tk.Label(
            self.panel,
            text="When you ready, you can start the game.",
            font=("Arial", 14, "bold"),
            fg=self.COLORS["text"],
            bg=self.COLORS["panel"],
        )
        self.message.pack(pady=(2, 5))

        self.hint = tk.Label(
            self.panel,
            text="Wait for the color changes.",
            font=("Arial", 10),
            fg=self.COLORS["muted"],
            bg=self.COLORS["panel"],
        )
        self.hint.pack()

        self.target = tk.Canvas(
            self.panel,
            width=250,
            height=220,
            bg=self.COLORS["panel"],
            highlightthickness=0,
            cursor="hand2",
        )
        self.target.pack(pady=(5, 10))
        self.target_circle = self.target.create_oval(
            25,
            10,
            225,
            210,
            fill=self.COLORS["neutral"],
            outline="",
            tags=("target",),
        )
        self.target_text = self.target.create_text(
            125,
            110,
            text="READY",
            fill=self.COLORS["text"],
            font=("Arial", 18, "bold"),
            tags=("target",),
        )
        self.target.tag_bind("target", "<Button-1>", self.on_target_click)

        self.start_button = tk.Button(
            self.panel,
            text="START",
            font=("Arial", 11, "bold"),
            fg="white",
            bg=self.COLORS["button"],
            activeforeground="white",
            activebackground=self.COLORS["button_active"],
            relief="flat",
            cursor="hand2",
            padx=32,
            pady=12,
            command=self.start_round,
        )
        self.start_button.pack(pady=(2, 5))

        tk.Label(
            self.content,
            text="The green light flashes very quickly! Press Esc to exit full screen.",
            font=("Arial", 9),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
        ).pack(pady=14)

    def exit_fullscreen(self, _event=None):
        self.root.attributes("-fullscreen", False)

    def start_round(self):
        self.cancel_timers()
        self.state = "red"
        self.message.config(text="Wait...")
        self.hint.config(text="Wait on red, no early clicking!")
        self.set_target_color("red", "Wait")
        self.start_button.config(text="Try again")

        delay_ms = random.randint(
            self.MIN_WAIT_SECONDS * 1000,
            self.MAX_WAIT_SECONDS * 1000,
        )
        self.wait_timer = self.root.after(delay_ms, self.show_green)

    def show_green(self):
        self.wait_timer = None
        if self.state != "red":
            return

        self.state = "green"
        self.message.config(text="NOW!")
        self.hint.config(text="GREEN! Click Now!")
        self.set_target_color("green", "Click Now!")
        green_duration_ms = random.randint(
            self.MIN_GREEN_DURATION_MS,
            self.MAX_GREEN_DURATION_MS,
        )
        self.green_timer = self.root.after(
            green_duration_ms,
            self.green_time_expired,
        )

    def on_target_click(self, _event=None):
        if self.state == "red":
            self.finish_round("lost", "Too slow, you missed it!")
        elif self.state == "green":
            self.finish_round("won", "U WON!")

    def green_time_expired(self):
        self.green_timer = None
        if self.state == "green":
            self.finish_round("missed", "Times up! Try again...")

    def finish_round(self, state, message):
        self.cancel_timers()
        self.state = state
        self.message.config(text=message)
        self.hint.config(text="Press the button to start a new round")
        if state == "won":
            self.set_target_color("green", "U WON!")
        elif state == "lost":
            self.set_target_color("red", "Too Soon");
        else:
            self.set_target_color("neutral", "Times Up!");

    def set_target_color(self, color, text):
        self.target.itemconfig(self.target_circle, fill=self.COLORS[color])
        self.target.itemconfig(self.target_text, text=text)

    def cancel_timers(self):
        if self.wait_timer is not None:
            self.root.after_cancel(self.wait_timer)
            self.wait_timer = None
        if self.green_timer is not None:
            self.root.after_cancel(self.green_timer)
            self.green_timer = None


if __name__ == "__main__":
    window = tk.Tk()
    game = ReactionGame(window)
    window.mainloop()
