import time
import tkinter as tk
from tkinter import ttk, filedialog

from algorithms import ALGORITHMS, ALGORITHM_INFO
from config import (
    APP_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    CANVAS_BG,
    BAR_COLOR,
    COMPARE_COLOR,
    SWAP_COLOR,
    SORTED_COLOR,
    FOUND_COLOR,
    TEXT_COLOR,
    MUTED_TEXT,
    PANEL_BG,
    ROOT_BG,
    CARD_BG,
    BORDER_COLOR,
    DEFAULT_ARRAY_SIZE,
    MIN_ARRAY_SIZE,
    MAX_ARRAY_SIZE,
    DEFAULT_SPEED,
    MIN_SPEED,
    MAX_SPEED,
    DEFAULT_SEARCH_TARGET,
)
from data import DataManager
from utils import safe_int, format_seconds
from test_mode import get_test_data, get_default_target, validate_algorithm_result
from explanations import get_algorithm_overview, build_step_explanation
from ui_components import make_button, make_card, create_info_row
from render_engine import draw_data
from custom_loader import controlled_check, run_in_sandbox


class AlgorithmVisualizerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=ROOT_BG)
        self.root.minsize(1280, 760)

        self.algorithm_name = tk.StringVar(value="Bubble Sort")
        self.status_text = tk.StringVar(value="Ready.")
        self.speed_value = tk.IntVar(value=DEFAULT_SPEED)
        self.size_value = tk.IntVar(value=DEFAULT_ARRAY_SIZE)
        self.search_target = tk.StringVar(value=str(DEFAULT_SEARCH_TARGET))

        self.stats_steps = tk.StringVar(value="0")
        self.stats_comparisons = tk.StringVar(value="0")
        self.stats_swaps = tk.StringVar(value="0")
        self.stats_elapsed = tk.StringVar(value="0.00s")

        self.complexity_best = tk.StringVar(value="-")
        self.complexity_avg = tk.StringVar(value="-")
        self.complexity_worst = tk.StringVar(value="-")
        self.complexity_space = tk.StringVar(value="-")
        self.algorithm_type = tk.StringVar(value="-")

        self.variables_text = tk.StringVar(value="No variables yet.")
        self.overview_text = tk.StringVar(value="Algoritma açıklaması burada görünecek.")
        self.why_algorithm_text = tk.StringVar(value="Bu algoritmanın önemi burada görünecek.")
        self.step_title_text = tk.StringVar(value="Current Step")
        self.step_explanation_text = tk.StringVar(value="Adım açıklaması burada görünecek.")
        self.step_why_text = tk.StringVar(value="Bu adımın neden önemli olduğu burada görünecek.")
        self.custom_file_text = tk.StringVar(value="No custom file selected.")
        self.inline_result_text = tk.StringVar(value="No custom check run yet.")

        self.data_manager = DataManager(DEFAULT_ARRAY_SIZE)

        self.is_running = False
        self.is_paused = False
        self.generator = None
        self.after_id = None
        self.start_time = None
        self.pause_started_at = None
        self.total_paused_time = 0.0

        self.history = []
        self.current_step_index = -1

        self.test_mode_enabled = False
        self.original_test_data = []

        self.custom_file_path = None
        self.custom_states = []
        self.custom_mode = False

        self._build_ui()
        self.refresh_algorithm_info()
        self.apply_idle_state(self.data_manager.get_data(), "Ready. Random data generated.")

    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        header = tk.Frame(self.root, bg=PANEL_BG, padx=14, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text="CBORN Algorithm Visualizer",
            fg="white",
            bg=PANEL_BG,
            font=("Segoe UI", 24, "bold")
        ).grid(row=0, column=0, columnspan=12, sticky="w", pady=(0, 10))

        tk.Label(
            header,
            text="Algorithm:",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=("Segoe UI", 12, "bold")
        ).grid(row=1, column=0, sticky="w", padx=(0, 8))

        self.algo_combo = ttk.Combobox(
            header,
            textvariable=self.algorithm_name,
            values=list(ALGORITHMS.keys()),
            state="readonly",
            width=20
        )
        self.algo_combo.grid(row=1, column=1, sticky="w", padx=(0, 12))
        self.algo_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        self.start_btn = make_button(header, "Start", self.start_sorting, "#16a34a")
        self.start_btn.grid(row=1, column=2, padx=6)

        self.pause_btn = make_button(header, "Pause", self.pause_sorting, "#f59e0b")
        self.pause_btn.grid(row=1, column=3, padx=6)

        self.resume_btn = make_button(header, "Resume", self.resume_sorting, "#0284c7")
        self.resume_btn.grid(row=1, column=4, padx=6)

        self.stop_btn = make_button(header, "Stop", self.stop_sorting, "#dc2626")
        self.stop_btn.grid(row=1, column=5, padx=6)

        self.reset_btn = make_button(header, "Reset", self.reset_data, "#2563eb")
        self.reset_btn.grid(row=1, column=6, padx=6)

        self.random_btn = make_button(header, "Random Data", self.generate_new_data, "#7c3aed")
        self.random_btn.grid(row=1, column=7, padx=6)

        self.test_btn = make_button(header, "Load Test", self.load_test_data, "#9333ea")
        self.test_btn.grid(row=1, column=8, padx=6)

        self.validate_btn = make_button(header, "Validate", self.validate_current_result, "#059669")
        self.validate_btn.grid(row=1, column=9, padx=6)

        self.load_custom_btn = make_button(header, "Load Custom", self.load_custom_file, "#6d28d9")
        self.load_custom_btn.grid(row=1, column=10, padx=6)

        tk.Label(
            header,
            text="Array Size:",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=("Segoe UI", 12, "bold")
        ).grid(row=2, column=0, sticky="w", pady=(12, 0))

        self.size_slider = tk.Scale(
            header,
            from_=MIN_ARRAY_SIZE,
            to=MAX_ARRAY_SIZE,
            orient="horizontal",
            variable=self.size_value,
            command=self.on_size_change,
            bg=PANEL_BG,
            fg=TEXT_COLOR,
            highlightthickness=0,
            troughcolor="#1f2937",
            length=220
        )
        self.size_slider.grid(row=2, column=1, columnspan=2, sticky="w", pady=(8, 0))

        tk.Label(
            header,
            text="Speed:",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=("Segoe UI", 12, "bold")
        ).grid(row=2, column=3, sticky="w", pady=(12, 0))

        self.speed_slider = tk.Scale(
            header,
            from_=MIN_SPEED,
            to=MAX_SPEED,
            orient="horizontal",
            variable=self.speed_value,
            bg=PANEL_BG,
            fg=TEXT_COLOR,
            highlightthickness=0,
            troughcolor="#1f2937",
            length=220
        )
        self.speed_slider.grid(row=2, column=4, columnspan=2, sticky="w", pady=(8, 0))

        tk.Label(
            header,
            text="Search Target:",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=("Segoe UI", 12, "bold")
        ).grid(row=2, column=6, sticky="w", pady=(12, 0))

        self.target_entry = tk.Entry(header, textvariable=self.search_target, width=12, font=("Segoe UI", 11))
        self.target_entry.grid(row=2, column=7, sticky="w", pady=(10, 0))

        self.controlled_btn = make_button(header, "Controlled", self.run_controlled_check, "#b45309")
        self.controlled_btn.grid(row=2, column=8, padx=6, pady=(8, 0))

        self.sandbox_btn = make_button(header, "Sandbox", self.run_custom_sandbox, "#0f766e")
        self.sandbox_btn.grid(row=2, column=9, padx=6, pady=(8, 0))

        tk.Label(
            header,
            textvariable=self.custom_file_text,
            fg=MUTED_TEXT,
            bg=PANEL_BG,
            font=("Consolas", 10)
        ).grid(row=2, column=10, columnspan=2, sticky="w", padx=6, pady=(8, 0))

        self.inline_result_label = tk.Label(
            header,
            textvariable=self.inline_result_text,
            fg="#fee2e2",
            bg="#7f1d1d",
            font=("Consolas", 10, "bold"),
            anchor="w",
            justify="left",
            padx=10,
            pady=8,
            wraplength=520
        )
        self.inline_result_label.grid(row=3, column=6, columnspan=6, sticky="ew", padx=6, pady=(10, 0))
        self.inline_result_label.grid_remove()

        body = tk.Frame(self.root, bg=ROOT_BG)
        body.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        left_panel = tk.Frame(body, bg=ROOT_BG)
        left_panel.pack(side="left", fill="both", expand=True)

        right_panel = tk.Frame(body, bg=ROOT_BG, width=360)
        right_panel.pack(side="right", fill="y", padx=(12, 0))
        right_panel.pack_propagate(False)

        self.canvas = tk.Canvas(
            left_panel,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )
        self.canvas.pack(fill="both", expand=True)

        stats_card = make_card(right_panel, "Stats", CARD_BG, BORDER_COLOR)
        create_info_row(stats_card, "Steps", self.stats_steps, CARD_BG, MUTED_TEXT, TEXT_COLOR)
        create_info_row(stats_card, "Comparisons", self.stats_comparisons, CARD_BG, MUTED_TEXT, TEXT_COLOR)
        create_info_row(stats_card, "Swaps", self.stats_swaps, CARD_BG, MUTED_TEXT, TEXT_COLOR)
        create_info_row(stats_card, "Elapsed", self.stats_elapsed, CARD_BG, MUTED_TEXT, TEXT_COLOR)

        complexity_card = make_card(right_panel, "Complexity", CARD_BG, BORDER_COLOR)
        create_info_row(complexity_card, "Type", self.algorithm_type, CARD_BG, MUTED_TEXT, TEXT_COLOR)
        create_info_row(complexity_card, "Best", self.complexity_best, CARD_BG, MUTED_TEXT, TEXT_COLOR)
        create_info_row(complexity_card, "Average", self.complexity_avg, CARD_BG, MUTED_TEXT, TEXT_COLOR)
        create_info_row(complexity_card, "Worst", self.complexity_worst, CARD_BG, MUTED_TEXT, TEXT_COLOR)
        create_info_row(complexity_card, "Space", self.complexity_space, CARD_BG, MUTED_TEXT, TEXT_COLOR)

        variables_card = make_card(right_panel, "Variables", CARD_BG, BORDER_COLOR)
        tk.Label(
            variables_card,
            textvariable=self.variables_text,
            justify="left",
            anchor="nw",
            fg=TEXT_COLOR,
            bg=CARD_BG,
            font=("Consolas", 10),
            wraplength=300
        ).pack(fill="x", padx=10, pady=(0, 10))

        overview_card = make_card(right_panel, "Algorithm Overview", CARD_BG, BORDER_COLOR)
        tk.Label(
            overview_card,
            textvariable=self.overview_text,
            justify="left",
            anchor="nw",
            fg=TEXT_COLOR,
            bg=CARD_BG,
            font=("Segoe UI", 10),
            wraplength=300
        ).pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(
            overview_card,
            textvariable=self.why_algorithm_text,
            justify="left",
            anchor="nw",
            fg=MUTED_TEXT,
            bg=CARD_BG,
            font=("Segoe UI", 10, "italic"),
            wraplength=300
        ).pack(fill="x", padx=10, pady=(0, 10))

        explanation_card = make_card(right_panel, "Step Explanation", CARD_BG, BORDER_COLOR)
        tk.Label(
            explanation_card,
            textvariable=self.step_title_text,
            justify="left",
            anchor="nw",
            fg="white",
            bg=CARD_BG,
            font=("Segoe UI", 11, "bold"),
            wraplength=300
        ).pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(
            explanation_card,
            textvariable=self.step_explanation_text,
            justify="left",
            anchor="nw",
            fg=TEXT_COLOR,
            bg=CARD_BG,
            font=("Segoe UI", 10),
            wraplength=300
        ).pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(
            explanation_card,
            textvariable=self.step_why_text,
            justify="left",
            anchor="nw",
            fg=MUTED_TEXT,
            bg=CARD_BG,
            font=("Segoe UI", 10, "italic"),
            wraplength=300
        ).pack(fill="x", padx=10, pady=(0, 10))

        code_card = make_card(right_panel, "Code", CARD_BG, BORDER_COLOR)
        self.code_text = tk.Text(
            code_card,
            height=18,
            bg="#0b1220",
            fg="#cbd5e1",
            insertbackground="white",
            relief="flat",
            font=("Consolas", 10),
            wrap="none"
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.code_text.config(state="disabled")

        footer = tk.Frame(self.root, bg=PANEL_BG, padx=12, pady=8)
        footer.pack(fill="x")

        self.status_label = tk.Label(
            footer,
            textvariable=self.status_text,
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=("Consolas", 11)
        )
        self.status_label.pack(side="left")

        self.root.bind("<Configure>", self.on_resize)

    def run(self):
        self.root.mainloop()

    def show_inline_result(self, message, is_error=False):
        self.inline_result_text.set(message)

        if is_error:
            self.inline_result_label.config(bg="#7f1d1d", fg="#fee2e2")
        else:
            self.inline_result_label.config(bg="#14532d", fg="#dcfce7")

        self.inline_result_label.grid()

    def hide_inline_result(self):
        self.inline_result_label.grid_remove()

    def on_resize(self, event=None):
        if event and event.widget == self.root:
            data = self.data_manager.get_data()
            if self.current_step_index >= 0 and self.history:
                self.render_state(self.history[self.current_step_index], preserve_status=True)
            else:
                self.redraw(data)

    def redraw(self, data, active=None, swap=None, sorted_indices=None, found_indices=None):
        draw_data(
            self.canvas,
            data,
            TEXT_COLOR,
            BAR_COLOR,
            COMPARE_COLOR,
            SWAP_COLOR,
            SORTED_COLOR,
            FOUND_COLOR,
            active=active,
            swap=swap,
            sorted_indices=sorted_indices,
            found_indices=found_indices,
        )

    def on_size_change(self, value):
        if self.is_running or self.is_paused:
            return
        self.generate_new_data()

    def on_algorithm_change(self, event=None):
        self.custom_mode = False
        self.hide_inline_result()
        self.refresh_algorithm_info()
        self.generate_new_data()

    def refresh_algorithm_info(self):
        info = ALGORITHM_INFO[self.algorithm_name.get()]
        self.algorithm_type.set(info["type"].title())
        self.complexity_best.set(info["best"])
        self.complexity_avg.set(info["average"])
        self.complexity_worst.set(info["worst"])
        self.complexity_space.set(info["space"])
        self.set_code_text(info["code"])

        overview = get_algorithm_overview(self.algorithm_name.get())
        self.overview_text.set(overview["overview"])
        self.why_algorithm_text.set(overview["why"])

    def set_code_text(self, code):
        self.code_text.config(state="normal")
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert(tk.END, code)
        self.code_text.config(state="disabled")

    def apply_idle_state(self, data, message):
        self.data_manager.set_data(data)
        self.redraw(data)
        self.status_text.set(message)
        self.reset_stats()
        self.variables_text.set("No variables yet.")
        self.history = []
        self.current_step_index = -1
        self.step_title_text.set("Current Step")
        self.step_explanation_text.set("Henüz algoritma çalıştırılmadı. Başlatınca adım adım ne yaptığını burada göreceksin.")
        self.step_why_text.set("Algoritma çalıştığında bu adımın neden önemli olduğu burada açıklanacak.")

    def generate_new_data(self):
        self.stop_sorting(silent=True)
        self.hide_inline_result()
        self.test_mode_enabled = False
        self.original_test_data = []
        self.custom_mode = False

        algo_type = ALGORITHM_INFO[self.algorithm_name.get()]["type"]
        size = self.size_value.get()
        self.data_manager.regenerate(
            size,
            sorted_mode=(algo_type == "searching" and self.algorithm_name.get() == "Binary Search")
        )

        message = f"Generated new {'sorted ' if self.algorithm_name.get() == 'Binary Search' else ''}random data with {size} elements."
        self.apply_idle_state(self.data_manager.get_data(), message)

    def reset_data(self):
        self.stop_sorting(silent=True)
        self.hide_inline_result()

        if self.test_mode_enabled and self.original_test_data:
            self.data_manager.original_data = self.original_test_data[:]
            self.data_manager.current_data = self.original_test_data[:]
            self.apply_idle_state(self.data_manager.get_data(), "Test data reset to original state.")
            return

        self.data_manager.reset()
        self.apply_idle_state(self.data_manager.get_data(), "Data reset to original state.")

    def load_test_data(self):
        self.stop_sorting(silent=True)
        self.hide_inline_result()
        self.custom_mode = False

        algorithm_name = self.algorithm_name.get()
        algorithm_type = ALGORITHM_INFO[algorithm_name]["type"]

        test_data = get_test_data(algorithm_type, algorithm_name)
        self.original_test_data = test_data[:]
        self.test_mode_enabled = True

        self.data_manager.original_data = test_data[:]
        self.data_manager.current_data = test_data[:]

        if algorithm_type == "searching":
            self.search_target.set(str(get_default_target()))

        self.apply_idle_state(test_data, f"Test data loaded for {algorithm_name}: {test_data}")

    def validate_current_result(self):
        if self.current_step_index < 0 or not self.history:
            msg = "No completed test state to validate yet."
            self.status_text.set(msg)
            self.show_inline_result("❌ " + msg, is_error=True)
            return

        algorithm_name = self.algorithm_name.get()
        final_state = self.history[self.current_step_index]

        if self.test_mode_enabled and self.original_test_data:
            base_data = self.original_test_data[:]
        else:
            base_data = self.data_manager.original_data[:]

        target = None
        if ALGORITHM_INFO[algorithm_name]["type"] == "searching":
            target = safe_int(self.search_target.get(), DEFAULT_SEARCH_TARGET)

        is_valid, message = validate_algorithm_result(
            algorithm_name=algorithm_name,
            final_state=final_state,
            original_data=base_data,
            target=target
        )

        final_message = ("✅ " if is_valid else "❌ ") + message
        self.status_text.set(final_message)
        self.show_inline_result(final_message, is_error=not is_valid)

    def start_sorting(self):
        if self.is_running:
            return

        self.stop_sorting(silent=True)
        self.hide_inline_result()
        self.custom_mode = False
        data = self.data_manager.get_data()
        algorithm_name = self.algorithm_name.get()
        algorithm = ALGORITHMS[algorithm_name]

        if ALGORITHM_INFO[algorithm_name]["type"] == "searching":
            target = safe_int(self.search_target.get(), DEFAULT_SEARCH_TARGET)
            self.generator = algorithm(data, target)
        else:
            self.generator = algorithm(data)

        self.history = []
        self.current_step_index = -1
        self.is_running = True
        self.is_paused = False
        self.start_time = time.perf_counter()
        self.total_paused_time = 0.0
        self.pause_started_at = None
        self.status_text.set(f"{algorithm_name} started.")
        self.animate()

    def pause_sorting(self):
        if not self.is_running:
            return
        self.is_running = False
        self.is_paused = True
        self.pause_started_at = time.perf_counter()
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.status_text.set("Paused.")

    def resume_sorting(self):
        if not self.is_paused or self.generator is None:
            return
        self.is_running = True
        self.is_paused = False
        if self.pause_started_at is not None:
            self.total_paused_time += time.perf_counter() - self.pause_started_at
            self.pause_started_at = None
        self.status_text.set("Resumed.")
        self.animate()

    def stop_sorting(self, silent=False):
        self.is_running = False
        self.is_paused = False
        self.generator = None
        self.pause_started_at = None
        self.total_paused_time = 0.0
        self.start_time = None

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        if not silent:
            self.status_text.set("Stopped.")

    def animate(self):
        if not self.is_running or self.generator is None:
            return

        try:
            step = next(self.generator)
            self.history.append(step)
            self.current_step_index += 1
            self.render_state(step)
            self.after_id = self.root.after(self.get_delay(), self.animate)

        except StopIteration:
            self.is_running = False
            self.generator = None
            self.after_id = None

            if self.history:
                self.render_state(self.history[-1], preserve_status=False)

            finish_message = "Custom program finished." if self.custom_mode else f"{self.algorithm_name.get()} finished."
            self.status_text.set(finish_message)

    def render_state(self, step, preserve_status=False):
        new_data = step.get("data", [])
        self.data_manager.set_data(new_data)

        self.redraw(
            new_data,
            active=step.get("active", []),
            swap=step.get("swap", []),
            sorted_indices=step.get("sorted_indices", []),
            found_indices=step.get("found_indices", []),
        )

        if not preserve_status:
            self.status_text.set(step.get("message", ""))

        stats = step.get("stats", {})
        self.stats_steps.set(str(stats.get("steps", 0)))
        self.stats_comparisons.set(str(stats.get("comparisons", 0)))
        self.stats_swaps.set(str(stats.get("swaps", 0)))
        self.stats_elapsed.set(self.get_elapsed_text())

        variables = step.get("variables", {})
        self.variables_text.set(
            "\n".join(f"{k} = {v}" for k, v in variables.items()) if variables else "No variables in this step."
        )

        if self.custom_mode:
            self.step_title_text.set("Custom Step")

            message = step.get("message", "Custom step running.")
            variables = step.get("variables", {})

            if variables:
                var_text = ", ".join(f"{k}={v}" for k, v in variables.items())
                self.step_explanation_text.set(f"{message}\nVariables: {var_text}")
            else:
                self.step_explanation_text.set(message)

            self.step_why_text.set(
                "Bu açıklama custom programın ürettiği state bilgisine göre gösteriliyor. "
                "Yani burada gördüğün anlatım doğrudan seçtiğin özel algoritmadan geliyor."
            )
        else:
            explanation = build_step_explanation(self.algorithm_name.get(), step)
            self.step_title_text.set(explanation["title"])
            self.step_explanation_text.set(explanation["explanation"])
            self.step_why_text.set(explanation["why"])

    def get_elapsed_text(self):
        if self.start_time is None:
            return "0.00s"
        elapsed = time.perf_counter() - self.start_time - self.total_paused_time
        return format_seconds(max(0.0, elapsed))

    def reset_stats(self):
        self.stats_steps.set("0")
        self.stats_comparisons.set("0")
        self.stats_swaps.set("0")
        self.stats_elapsed.set("0.00s")

    def get_delay(self):
        return max(1, 201 - self.speed_value.get())

    def load_custom_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Custom Python File",
            filetypes=[("Python Files", "*.py")]
        )
        if not file_path:
            return

        self.custom_file_path = file_path
        self.custom_file_text.set(file_path.split("/")[-1].split("\\")[-1])

        msg = "Custom file selected. Run Controlled check first."
        self.status_text.set(msg)
        self.show_inline_result("ℹ️ " + msg, is_error=False)

    def run_controlled_check(self):
        if not self.custom_file_path:
            msg = "No custom file selected."
            self.status_text.set(msg)
            self.show_inline_result("❌ " + msg, is_error=True)
            return

        ok, message = controlled_check(self.custom_file_path)
        final_message = ("✅ " if ok else "❌ ") + message

        self.status_text.set(final_message)
        self.show_inline_result(final_message, is_error=not ok)

    def run_custom_sandbox(self):
        if not self.custom_file_path:
            msg = "No custom file selected."
            self.status_text.set(msg)
            self.show_inline_result("❌ " + msg, is_error=True)
            return

        ok, result = run_in_sandbox(self.custom_file_path, self.data_manager.get_data())

        if not ok:
            final_message = "❌ " + result.get("message", "Sandbox failed.")
            self.status_text.set(final_message)
            self.show_inline_result(final_message, is_error=True)
            return

        self.custom_states = result.get("states", [])
        meta = result.get("meta", {})

        if not self.custom_states:
            final_message = "❌ Sandbox returned no states."
            self.status_text.set(final_message)
            self.show_inline_result(final_message, is_error=True)
            return

        self.custom_mode = True
        self.history = self.custom_states[:]
        self.current_step_index = -1
        self.start_time = time.perf_counter()
        self.total_paused_time = 0.0
        self.pause_started_at = None

        self.overview_text.set(meta.get("overview", "Custom algorithm loaded."))
        self.why_algorithm_text.set(meta.get("why", "Custom algorithm explanation not provided."))
        self.set_code_text("Custom file loaded via sandbox.")
        self.algorithm_type.set("Custom")
        self.complexity_best.set(meta.get("best", "-"))
        self.complexity_avg.set(meta.get("average", "-"))
        self.complexity_worst.set(meta.get("worst", "-"))
        self.complexity_space.set(meta.get("space", "-"))

        success_msg = "✅ Sandbox execution completed. Replaying custom states."
        self.status_text.set(success_msg)
        self.show_inline_result(success_msg, is_error=False)
        self.play_custom_states()

    def play_custom_states(self):
        if self.current_step_index + 1 >= len(self.custom_states):
            self.status_text.set("Custom program finished.")
            return

        self.current_step_index += 1
        step = self.custom_states[self.current_step_index]
        self.render_state(step)
        self.after_id = self.root.after(self.get_delay(), self.play_custom_states)