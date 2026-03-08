import tkinter as tk
from tkinter import scrolledtext
from custom_loader import analyze_python_file


def test_broken_file(root, file_path, ROOT_BG, PANEL_BG):
    """Bozuk dosyayi analiz et, sol kod + sag hata penceresi ac"""
    if not file_path:
        return

    # Dosyayi oku
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_lines = f.readlines()
    except Exception:
        source_lines = ["# Dosya okunamadi\n"]

    # Analiz yap
    analysis = analyze_python_file(file_path)

    # Hatali satirlari topla
    error_lines = set()
    warning_lines = set()

    for err in analysis.get("errors", []):
        line_num = _extract_line_number(err)
        if line_num:
            error_lines.add(line_num)

    for warn in analysis.get("warnings", []):
        line_num = _extract_line_number(warn)
        if line_num:
            warning_lines.add(line_num)

    # Pencere olustur
    window = tk.Toplevel(root)
    window.title("Code Analysis Report")
    window.geometry("1100x600")
    window.configure(bg=ROOT_BG)
    window.minsize(900, 500)

    # Header
    header = tk.Frame(window, bg=PANEL_BG, padx=12, pady=10)
    header.pack(fill="x")

    filename = file_path.split("/")[-1].split("\\")[-1]
    tk.Label(
        header,
        text=f"Code Analysis: {filename}",
        fg="white", bg=PANEL_BG,
        font=("Segoe UI", 14, "bold")
    ).pack(side="left")

    summary = analysis.get("summary", "")
    summary_color = "#ef4444" if analysis["errors"] else "#22c55e"
    tk.Label(
        header,
        text=summary,
        fg=summary_color, bg=PANEL_BG,
        font=("Segoe UI", 11, "bold")
    ).pack(side="right")

    # Body - sol kod, sag hatalar
    body = tk.Frame(window, bg=ROOT_BG)
    body.pack(fill="both", expand=True, padx=10, pady=10)

    # ========== SOL: KOD GORUNUMU ==========
    left_frame = tk.Frame(body, bg=ROOT_BG)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

    tk.Label(
        left_frame, text="SOURCE CODE",
        fg="#94a3b8", bg=ROOT_BG,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(0, 4))

    code_text = tk.Text(
        left_frame,
        bg="#0b1220", fg="#cbd5e1",
        font=("Consolas", 10),
        wrap="none", relief="flat",
        insertbackground="white",
        selectbackground="#334155"
    )
    code_text.pack(fill="both", expand=True)

    # Scrollbar
    code_scroll_y = tk.Scrollbar(code_text, orient="vertical", command=code_text.yview)
    code_scroll_y.pack(side="right", fill="y")
    code_text.configure(yscrollcommand=code_scroll_y.set)

    code_scroll_x = tk.Scrollbar(code_text, orient="horizontal", command=code_text.xview)
    code_scroll_x.pack(side="bottom", fill="x")
    code_text.configure(xscrollcommand=code_scroll_x.set)

    # Tag'leri tanimla
    code_text.tag_configure("error_line", background="#3b1111", foreground="#fca5a5")
    code_text.tag_configure("warning_line", background="#3b2e11", foreground="#fde68a")
    code_text.tag_configure("normal_line", foreground="#cbd5e1")
    code_text.tag_configure("line_number", foreground="#475569")

    # Kodu satirlariyla yaz
    for i, line in enumerate(source_lines, 1):
        line_num_str = f"{i:4d}  "
        code_text.insert("end", line_num_str, "line_number")

        if i in error_lines:
            code_text.insert("end", line.rstrip("\n") + "\n", "error_line")
        elif i in warning_lines:
            code_text.insert("end", line.rstrip("\n") + "\n", "warning_line")
        else:
            code_text.insert("end", line.rstrip("\n") + "\n", "normal_line")

    code_text.config(state="disabled")

    # Ilk hataya scroll
    first_error = min(error_lines) if error_lines else (min(warning_lines) if warning_lines else None)
    if first_error:
        code_text.see(f"{first_error}.0")

    # ========== SAG: HATA LISTESI ==========
    right_frame = tk.Frame(body, bg=ROOT_BG, width=380)
    right_frame.pack(side="right", fill="y", padx=(5, 0))
    right_frame.pack_propagate(False)

    tk.Label(
        right_frame, text="ISSUES",
        fg="#94a3b8", bg=ROOT_BG,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(0, 4))

    issues_text = scrolledtext.ScrolledText(
        right_frame,
        bg="#0b1220", fg="#cbd5e1",
        font=("Consolas", 10),
        wrap="word", relief="flat"
    )
    issues_text.pack(fill="both", expand=True)

    issues_text.tag_configure("error_header", foreground="#ef4444", font=("Consolas", 11, "bold"))
    issues_text.tag_configure("warning_header", foreground="#f59e0b", font=("Consolas", 11, "bold"))
    issues_text.tag_configure("error_item", foreground="#fca5a5")
    issues_text.tag_configure("warning_item", foreground="#fde68a")
    issues_text.tag_configure("success", foreground="#22c55e", font=("Consolas", 12, "bold"))
    issues_text.tag_configure("separator", foreground="#334155")

    # Hatalari yaz
    errors = analysis.get("errors", [])
    warnings = analysis.get("warnings", [])

    if errors:
        issues_text.insert("end", f"ERRORS ({len(errors)})\n", "error_header")
        issues_text.insert("end", "=" * 40 + "\n", "separator")
        for i, err in enumerate(errors, 1):
            issues_text.insert("end", f"\n{i}. {err}\n", "error_item")
        issues_text.insert("end", "\n")

    if warnings:
        issues_text.insert("end", f"WARNINGS ({len(warnings)})\n", "warning_header")
        issues_text.insert("end", "=" * 40 + "\n", "separator")
        for i, warn in enumerate(warnings, 1):
            issues_text.insert("end", f"\n{i}. {warn}\n", "warning_item")
        issues_text.insert("end", "\n")

    if not errors and not warnings:
        issues_text.insert("end", "\nNO ISSUES FOUND!\n", "success")
        issues_text.insert("end", "\nFile is clean and ready to run.\n", "warning_item")

    issues_text.config(state="disabled")

    # ========== FOOTER ==========
    footer = tk.Frame(window, bg=PANEL_BG, padx=12, pady=8)
    footer.pack(fill="x")

    # Sayac
    count_text = f"Errors: {len(errors)}  |  Warnings: {len(warnings)}"
    tk.Label(
        footer, text=count_text,
        fg="#94a3b8", bg=PANEL_BG,
        font=("Consolas", 10)
    ).pack(side="left")

    tk.Button(
        footer, text="Close",
        command=window.destroy,
        bg="#dc2626", fg="white",
        font=("Segoe UI", 11, "bold"),
        padx=20, pady=6,
        relief="flat", cursor="hand2"
    ).pack(side="right")


def _extract_line_number(message):
    """Hata mesajindan satir numarasini cikar"""
    # "Line 5:" veya "at line 5" formatlarini yakala
    msg = message.lower()

    # "line X:" formati
    if "line " in msg:
        try:
            idx = msg.index("line ")
            rest = msg[idx + 5:]
            num_str = ""
            for ch in rest:
                if ch.isdigit():
                    num_str += ch
                else:
                    break
            if num_str:
                return int(num_str)
        except (ValueError, IndexError):
            pass

    return None