import os
import sys
import time
from args import parse_args, decide_mode
from archive import (
    archive_single_file,
    archive_directory_tree,
    unpack_archive_to_temporary,
    extract_archive_contents,
    generate_archive_filename
)


def execute_compression_operation(source_path: str, destination_path: str | None, compression_level: int | None):
    """Выполняет операцию сжатия файла или директории."""
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Источник не найден: {source_path!r}")

    if destination_path is None:
        destination_path = generate_archive_filename(source_path)
        print(f"Целевой архив не задан. Используется: {destination_path!r}")

    if os.path.isdir(source_path):
        archive_directory_tree(source_path, destination_path, compression_level)
    else:
        archive_single_file(source_path, destination_path, compression_level)


def execute_extraction_operation(archive_path: str, destination_path: str | None):
    """Выполняет операцию распаковки архива."""
    if not os.path.isfile(archive_path):
        raise FileNotFoundError(f"Архив не найден: {archive_path!r}")
    
    temporary_file = unpack_archive_to_temporary(archive_path)
    extract_archive_contents(temporary_file, archive_path, destination_path)


def main(argv=None):
    """Главная функция программы."""
    parsed_args = parse_args(argv)

    input_path = parsed_args.source
    output_path = parsed_args.destination
    enable_benchmark = parsed_args.benchmark
    compression_level = parsed_args.level

    operation_mode = decide_mode(input_path, output_path, parsed_args.extract)

    timer_start = time.perf_counter() if enable_benchmark else None

    try:
        if operation_mode == "compress":
            execute_compression_operation(input_path, output_path, compression_level)
        else:
            execute_extraction_operation(input_path, output_path)

    except Exception as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    finally:
        if enable_benchmark:
            execution_time = time.perf_counter() - timer_start
            print(f"Время выполнения: {execution_time:.3f} сек", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
