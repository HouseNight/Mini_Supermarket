from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def apply_default_style(root: tk.Widget | None = None) -> None:
    style = ttk.Style(root) if root else ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Primary colors
    PRIMARY = "#2563eb"
    PRIMARY_HOVER = "#1d4ed8"
    PRIMARY_LIGHT = "#dbeafe"
    DANGER = "#dc2626"
    DANGER_HOVER = "#b91c1c"
    SUCCESS = "#16a34a"
    SUCCESS_HOVER = "#15803d"
    SECONDARY = "#6366f1"
    SECONDARY_HOVER = "#4f46e5"
    NEUTRAL = "#1f2937"
    NEUTRAL_LIGHT = "#f3f4f6"
    BORDER = "#e5e7eb"

    # Main button style
    style.configure(
        "TButton",
        padding=(12, 10),
        font=("Segoe UI", 10),
        relief="flat",
        background="#e4e4e7",
        foreground=NEUTRAL,
    )
    style.map(
        "TButton",
        foreground=[("disabled", "#9ca3af")],
        background=[("active", "#d4d4d8"), ("pressed", "#d4d4d8")],
    )

    # Accent button (primary action)
    style.configure(
        "Accent.TButton",
        foreground="white",
        background=PRIMARY,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padding=(12, 10),
    )
    style.map(
        "Accent.TButton",
        background=[("active", PRIMARY_HOVER), ("pressed", PRIMARY_HOVER), ("disabled", "#93c5fd")],
        foreground=[("disabled", "#ffffff")],
    )

    # Danger button (destructive action)
    style.configure(
        "Danger.TButton",
        foreground="white",
        background=DANGER,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padding=(12, 10),
    )
    style.map(
        "Danger.TButton",
        background=[("active", DANGER_HOVER), ("pressed", DANGER_HOVER), ("disabled", "#fca5a5")],
        foreground=[("disabled", "#ffffff")],
    )

    # Success button
    style.configure(
        "Success.TButton",
        foreground="white",
        background=SUCCESS,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padding=(12, 10),
    )
    style.map(
        "Success.TButton",
        background=[("active", SUCCESS_HOVER), ("pressed", SUCCESS_HOVER), ("disabled", "#86efac")],
    )

    # Secondary button
    style.configure(
        "Secondary.TButton",
        foreground="white",
        background=SECONDARY,
        font=("Segoe UI", 10),
        relief="flat",
        padding=(10, 8),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", SECONDARY_HOVER), ("pressed", SECONDARY_HOVER)],
    )

    # Labels
    style.configure("TLabel", font=("Segoe UI", 10), foreground=NEUTRAL, background=NEUTRAL_LIGHT)
    style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground=NEUTRAL, background=NEUTRAL_LIGHT)
    style.configure("SubHeader.TLabel", font=("Segoe UI", 12, "bold"), foreground=PRIMARY, background=NEUTRAL_LIGHT)
    style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground=NEUTRAL, background=NEUTRAL_LIGHT)
    style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), foreground=NEUTRAL, background="#ffffff")
    style.configure("CardValue.TLabel", font=("Segoe UI", 20, "bold"), foreground=PRIMARY, background="#ffffff")
    style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#6b7280", background=NEUTRAL_LIGHT)
    style.configure("Badge.TLabel", font=("Segoe UI", 8, "bold"), foreground="white", background=SECONDARY)

    # Frames and containers
    style.configure(
        "Card.TFrame",
        background=NEUTRAL_LIGHT,
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Panel.TFrame",
        background="#ffffff",
        borderwidth=1,
        relief="solid",
    )
    style.configure(
        "Highlight.TFrame",
        background="#ffffff",
        borderwidth=2,
        relief="solid",
    )

    # Section/Group
    style.configure(
        "Section.TLabelframe",
        background="#ffffff",
        borderwidth=1,
        relief="solid",
    )
    style.configure(
        "Section.TLabelframe.Label",
        font=("Segoe UI", 12, "bold"),
        foreground=PRIMARY,
        background="#ffffff",
    )

    # Notebook (tabs)
    style.configure(
        "TNotebook",
        background=NEUTRAL_LIGHT,
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        padding=(16, 10),
        font=("Segoe UI", 10, "bold"),
        background="#e5e7eb",
        foreground=NEUTRAL,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", "#ffffff"), ("active", "#f3f4f6")],
        foreground=[("selected", PRIMARY)],
    )

    # Treeview
    style.configure(
        "Treeview",
        rowheight=32,
        fieldbackground="#ffffff",
        background="#ffffff",
        foreground=NEUTRAL,
        font=("Segoe UI", 10),
        borderwidth=1,
    )
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background="#f3f4f6",
        foreground=NEUTRAL,
    )
    style.map(
        "Treeview",
        background=[("selected", PRIMARY_LIGHT)],
        foreground=[("selected", NEUTRAL)],
    )

    # Entry
    style.configure(
        "TEntry",
        font=("Segoe UI", 10),
        foreground=NEUTRAL,
        padding=6,
    )

    # Combobox
    style.configure(
        "TCombobox",
        font=("Segoe UI", 10),
        foreground=NEUTRAL,
        padding=6,
    )

    # Separator
    style.configure("Separator", background=BORDER)

    if root:
        root.option_add("*Font", ("Segoe UI", 10))
        root.option_add("*Background", NEUTRAL_LIGHT)
        root.option_add("*Foreground", NEUTRAL)
