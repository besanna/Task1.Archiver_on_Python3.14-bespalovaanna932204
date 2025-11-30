import argparse
import os


def parse_args(argv=None):
    """Парсит аргументы командной строки."""
    argument_parser = argparse.ArgumentParser(
        prog="arch.py",
        description=(
            "Архиватор/распаковщик на Python 3.14\n"
            "Алгоритм по расширению: .zst -> zstd, .bz2 -> bz2\n"
            "Директории упаковываются через tarfile"
        ),
    )

    argument_parser.add_argument(
        "source",
        help="Источник: файл/директория (для сжатия) или архив (.zst/.bz2) для распаковки",
    )
    argument_parser.add_argument(
        "destination",
        nargs="?",
        help="Куда писать результат. При сжатии — целевой архив. При распаковке — файл/директория.",
    )

    argument_parser.add_argument(
        "-b", "--benchmark",
        action="store_true",
        help="Вывести время выполнения операции."
    )

    argument_parser.add_argument(
        "-x", "--extract",
        action="store_true",
        help="Принудительный режим распаковки"
    )

    argument_parser.add_argument(
        "--level",
        type=int,
        default=None,
        help="Уровень сжатия для Zstandard"
    )

    return argument_parser.parse_args(argv)


def decide_mode(input_path: str, output_path: str | None, extract_flag: bool):
    """Определяет режим работы: сжатие или распаковка."""
    if extract_flag:
        return "extract"

    is_compressed_file = os.path.isfile(input_path) and input_path.lower().endswith((".zst", ".bz2"))
    
    if is_compressed_file:
        if output_path and output_path.lower().endswith((".zst", ".bz2")):
            return "compress"
        return "extract"

    return "compress"
