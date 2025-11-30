from compression import bz2, zstd


def get_algorithm(file_path: str) -> str:
    """Определяет алгоритм сжатия по расширению файла."""
    path_lower = file_path.lower()
    if path_lower.endswith(".zst"):
        return "zstd"
    if path_lower.endswith(".bz2"):
        return "bz2"
    raise ValueError(
        f"Невозможно определить алгоритм по расширению: {file_path!r}. "
        f"Ожидается .zst или .bz2"
    )


def open_compressed(file_path: str, file_mode: str, compression_algorithm: str, compression_level=None):
    """Открывает файл с использованием указанного алгоритма сжатия."""
    if compression_algorithm == "zstd":
        return zstd.open(file_path, mode=file_mode, level=compression_level)
    elif compression_algorithm == "bz2":
        return bz2.open(file_path, mode=file_mode)
    else:
        raise ValueError(f"Неизвестный алгоритм: {compression_algorithm}")
