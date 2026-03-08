import random
from config import MIN_VALUE, MAX_VALUE


def generate_random_data(size: int) -> list[int]:
    return [random.randint(MIN_VALUE, MAX_VALUE) for _ in range(size)]


def generate_sorted_random_data(size: int) -> list[int]:
    return sorted(generate_random_data(size))


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def format_seconds(seconds: float) -> str:
    return f"{seconds:.2f}s"