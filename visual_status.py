from __future__ import annotations

from typing import Any, Iterable, Optional


def safe_len(value: Optional[Iterable[Any]]) -> int:
    if value is None:
        return 0
    try:
        return len(value)
    except Exception:
        count = 0
        for _ in value:
            count += 1
        return count


def normalize_mode_name(mode: Optional[str]) -> str:
    if not mode:
        return "Unknown"

    mode = str(mode).strip().lower()
    mapping = {
        "sandbox": "Sandbox",
        "controlled": "Controlled Path",
        "control": "Controlled Path",
        "kontrollu": "Controlled Path",
        "kontrollü": "Controlled Path",
    }
    return mapping.get(mode, mode.title())


def build_status_text(
    mode: str = "sandbox",
    *,
    selected: Any = "-",
    path: Optional[Iterable[Any]] = None,
    state: str = "Ready",
    extra: Optional[str] = None,
) -> str:
    mode_name = normalize_mode_name(mode)
    path_length = safe_len(path)
    text = f"Mode: {mode_name} | Selected: {selected} | Path Length: {path_length} | State: {state}"
    if extra:
        text += f" | {extra}"
    return text


def build_result_status(mode: str, result: Any) -> str:
    path = getattr(result, "path", None)
    state = getattr(result, "state", "Ready")
    selected = getattr(result, "selected", "-")
    extra = getattr(result, "extra", None)

    return build_status_text(
        mode=mode,
        selected=selected,
        path=path,
        state=state,
        extra=extra,
    )


def update_status_label(label, text: str) -> None:
    try:
        label.configure(text=text)
    except Exception:
        label.config(text=text)


def set_ready(label, mode: str = "sandbox") -> None:
    update_status_label(label, build_status_text(mode=mode, state="Ready"))


def set_running(label, mode: str = "sandbox", selected: Any = "-") -> None:
    update_status_label(label, build_status_text(mode=mode, selected=selected, state="Running"))


def set_finished(label, mode: str = "sandbox", selected: Any = "-", path: Optional[Iterable[Any]] = None) -> None:
    update_status_label(
        label,
        build_status_text(
            mode=mode,
            selected=selected,
            path=path,
            state="Finished",
        ),
    )