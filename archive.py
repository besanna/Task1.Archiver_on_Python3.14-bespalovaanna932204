import os
import tempfile
import tarfile
from algorithms import get_algorithm, open_compressed
from display import progress_bar

# Размер блока для чтения/записи
BUFFER_SIZE = 1024 * 1024


def generate_archive_filename(input_path: str) -> str:
    """Генерирует имя архива на основе исходного пути."""
    filename = os.path.basename(os.path.normpath(input_path))
    if os.path.isdir(input_path):
        filename += ".tar"
    return filename + ".zst"


def transfer_data_with_status(input_stream, output_stream, label="", expected_size=None):
    """Копирует данные из входного потока в выходной с отображением прогресса."""
    transferred = 0
    while True:
        data_block = input_stream.read(BUFFER_SIZE)
        if not data_block:
            break
        output_stream.write(data_block)
        transferred += len(data_block)
        progress_bar(transferred, expected_size, label)
    print()


def archive_single_file(input_file: str, output_file: str, compression_level=None):
    """Сжимает один файл в архив."""
    compression_type = get_algorithm(output_file)
    file_size = os.path.getsize(input_file)
    print(f"Сжатие файла {input_file!r} -> {output_file!r} ({compression_type})")

    with open(input_file, "rb") as input_handle, \
         open_compressed(output_file, "wb", compression_type, compression_level) as output_handle:
        transfer_data_with_status(input_handle, output_handle, label="compress", expected_size=file_size)


def archive_directory_tree(input_dir: str, output_file: str, compression_level=None):
    """Архивирует директорию в tar и сжимает."""
    compression_type = get_algorithm(output_file)
    print(f"Архивация директории {input_dir!r} -> tar -> {output_file!r} ({compression_type})")

    class ProgressTracker:
        """Обертка для отслеживания прогресса записи."""
        def __init__(self, target_stream):
            self.target_stream = target_stream
            self.bytes_written = 0

        def write(self, data: bytes):
            bytes_count = self.target_stream.write(data)
            self.bytes_written += bytes_count
            progress_bar(self.bytes_written, None, prefix="tar+compress")
            return bytes_count

        def flush(self):
            return self.target_stream.flush()

    with open_compressed(output_file, "wb", compression_type, compression_level) as compressed_stream:
        progress_wrapper = ProgressTracker(compressed_stream)
        with tarfile.open(fileobj=progress_wrapper, mode="w|") as tar_archive:
            tar_archive.add(input_dir, arcname=os.path.basename(input_dir))
    print()


def unpack_archive_to_temporary(archive_file: str) -> str:
    """Распаковывает архив во временный файл."""
    compression_type = get_algorithm(archive_file)
    archive_size = os.path.getsize(archive_file)

    print(f"Распаковка архива {archive_file!r} ({compression_type}) -> временный файл")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        with open_compressed(archive_file, "rb", compression_type) as archive_stream:
            transfer_data_with_status(archive_stream, temp_file, label="decompress", expected_size=archive_size)

    return temp_file_path


def _remove_compression_extensions(filename: str) -> str:
    """Удаляет расширения сжатия из имени файла."""
    result = filename
    for ext in (".zst", ".bz2"):
        if result.endswith(ext):
            result = result[:-len(ext)]
    return result


def _determine_output_path(archive_path: str, temp_file_path: str, user_specified_path: str | None) -> str:
    """Определяет путь для извлечения файлов."""
    if user_specified_path is not None:
        return user_specified_path
    
    base_name = os.path.basename(archive_path)
    base_name = _remove_compression_extensions(base_name)
    if base_name.endswith(".tar"):
        base_name = base_name[:-4]
    
    return os.path.join(os.path.dirname(archive_path), base_name)


def extract_archive_contents(temp_file_path: str, archive_path: str, output_path: str | None):
    """Извлекает содержимое архива из временного файла."""
    contains_tar = tarfile.is_tarfile(temp_file_path)

    if contains_tar:
        output_directory = _determine_output_path(archive_path, temp_file_path, output_path)
        print(f"Обнаружен TAR. Извлечение в {output_directory!r}")
        os.makedirs(output_directory, exist_ok=True)
        with tarfile.open(temp_file_path, "r:*") as tar_archive:
            tar_archive.extractall(output_directory)
        os.remove(temp_file_path)
    else:
        output_file = _determine_output_path(archive_path, temp_file_path, output_path)
        print(f"Запись распакованного файла -> {output_file!r}")
        output_parent = os.path.dirname(os.path.abspath(output_file)) or "."
        os.makedirs(output_parent, exist_ok=True)
        os.replace(temp_file_path, output_file)
