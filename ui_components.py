import tkinter as tk


def make_button(parent, text, command, bg):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg="white",
        activebackground=bg,
        activeforeground="white",
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        width=11,
        padx=6,
        pady=6
    )


def make_card(parent, title, card_bg, border_color):
    card = tk.Frame(
        parent,
        bg=card_bg,
        highlightthickness=1,
        highlightbackground=border_color
    )
    card.pack(fill="x", pady=(0, 10))

    title_label = tk.Label(
        card,
        text=title,
        fg="white",
        bg=card_bg,
        font=("Segoe UI", 13, "bold")
    )
    title_label.pack(anchor="w", padx=10, pady=(10, 8))
    return card


def create_info_row(parent, label_text, value_var, card_bg, muted_text, text_color):
    row = tk.Frame(parent, bg=card_bg)
    row.pack(fill="x", padx=10, pady=2)

    tk.Label(
        row,
        text=label_text,
        fg=muted_text,
        bg=card_bg,
        font=("Segoe UI", 10, "bold")
    ).pack(side="left")

    tk.Label(
        row,
        textvariable=value_var,
        fg=text_color,
        bg=card_bg,
        font=("Consolas", 10)
    ).pack(side="right")