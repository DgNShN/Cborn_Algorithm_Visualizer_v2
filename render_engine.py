def draw_data(
    canvas,
    data,
    text_color,
    bar_color,
    compare_color,
    swap_color,
    sorted_color,
    found_color,
    active=None,
    swap=None,
    sorted_indices=None,
    found_indices=None,
):
    active = active or []
    swap = swap or []
    sorted_indices = sorted_indices or []
    found_indices = found_indices or []

    canvas.delete("all")

    if not data:
        return

    canvas_width = max(canvas.winfo_width(), 1)
    canvas_height = max(canvas.winfo_height(), 1)

    left_pad = 22
    right_pad = 22
    top_pad = 36
    bottom_pad = 50

    draw_width = canvas_width - left_pad - right_pad
    draw_height = canvas_height - top_pad - bottom_pad

    max_val = max(data) if data else 1
    n = len(data)
    bar_width = draw_width / max(1, n)
    font_size = 9 if n <= 50 else 7

    for i, value in enumerate(data):
        x0 = left_pad + i * bar_width
        x1 = left_pad + (i + 1) * bar_width - 2

        normalized_height = (value / max_val) * draw_height if max_val else 0
        y0 = top_pad + (draw_height - normalized_height)
        y1 = top_pad + draw_height

        color = bar_color
        if i in found_indices:
            color = found_color
        elif i in sorted_indices:
            color = sorted_color
        elif i in swap:
            color = swap_color
        elif i in active:
            color = compare_color

        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

        if n <= 60:
            canvas.create_text(
                (x0 + x1) / 2,
                y0 - 10,
                text=str(value),
                fill=text_color,
                font=("Consolas", font_size)
            )

    canvas.create_text(
        10,
        10,
        anchor="nw",
        text=f"Elements: {n}",
        fill=text_color,
        font=("Segoe UI", 10, "bold")
    )