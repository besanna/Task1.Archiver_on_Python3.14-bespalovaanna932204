import sys


def format_bytes(bytes_count: int) -> str:
    """Форматирует размер в байтах в читаемый вид."""
    units = ("B", "KiB", "MiB", "GiB")
    value = float(bytes_count)
    for unit in units:
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TiB"


def progress_bar(processed: int, total: int | None, prefix=""):
    """Отображает прогресс-бар обработки данных."""
    if total:
        completion_ratio = processed / total
        bar_width = 30
        filled_chars = int(completion_ratio * bar_width)
        progress_bar_str = "#" * filled_chars + "-" * (bar_width - filled_chars)
        percentage = completion_ratio * 100
        sys.stdout.write(
            f"\r{prefix} [{progress_bar_str}] {percentage:5.1f}% "
            f"({format_bytes(processed)}/{format_bytes(total)})"
        )
    else:
        sys.stdout.write(f"\r{prefix} {format_bytes(processed)} processed")

    sys.stdout.flush()
