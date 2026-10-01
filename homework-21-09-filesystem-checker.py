import os
import stat


def filesystem_type(path):
    """Название ФС в Linux из таблицы монтирования текущего процесса."""
    path = os.path.realpath(path)
    best_mount, fs_type = "", "не удалось определить"
    try:
        with open("/proc/self/mountinfo", encoding="utf-8") as mounts:
            for line in mounts:
                left, right = line.rstrip().split(" - ", 1)
                mount = left.split()[4]
                # В таблице пробелы и некоторые символы экранированы.
                for code, char in ((r"\040", " "), (r"\011", "\t"),
                                   (r"\012", "\n"), (r"\134", "\\")):
                    mount = mount.replace(code, char)
                if path == mount or path.startswith(mount.rstrip("/") + "/"):
                    if len(mount) >= len(best_mount):
                        best_mount, fs_type = mount, right.split()[0]
    except (OSError, ValueError, IndexError):
        pass
    return fs_type


def show_filesystem_info(path):
    """Выводит статистику ФС, содержащей указанный путь."""
    print("\nФАЙЛОВАЯ СИСТЕМА:", os.path.abspath(path))
    if not hasattr(os, "statvfs"):
        print("os.statvfs недоступна: запустите программу в Linux/Unix.")
        return
    try:
        fs = os.statvfs(path)
        unit = fs.f_frsize or fs.f_bsize
        print("Тип файловой системы:", filesystem_type(path))
        print("Размер блока:", fs.f_bsize, "байт")
        print("Единица учёта блоков:", unit, "байт")
        print("Количество блоков:", fs.f_blocks)
        print("Свободных блоков всего:", fs.f_bfree)
        print("Блоков, доступных пользователю:", fs.f_bavail)
        print("Количество inode:", fs.f_files)
        print("Свободных inode:", fs.f_ffree)
        print("Inode, доступных пользователю:", fs.f_favail)
        print("Общий объём:", fs.f_blocks * unit, "байт")
        print("Свободный объём:", fs.f_bfree * unit, "байт")
        print("Максимальная длина имени:", fs.f_namemax)
        print("Флаги монтирования:", fs.f_flag)
    except OSError as error:
        print("Ошибка чтения информации о ФС:", error)


def show_file_info(path):
    """lstat показывает саму символическую ссылку, а не её цель."""
    print("\nФАЙЛ:", os.path.abspath(path))
    try:
        info = os.lstat(path)
        kinds = ((stat.S_ISREG, "обычный файл"),
                 (stat.S_ISDIR, "каталог"),
                 (stat.S_ISLNK, "символическая ссылка"),
                 (stat.S_ISCHR, "символьное устройство"),
                 (stat.S_ISBLK, "блочное устройство"),
                 (stat.S_ISFIFO, "именованный канал"),
                 (stat.S_ISSOCK, "сокет"))
        kind = next((name for check, name in kinds if check(info.st_mode)),
                    "неизвестный тип")
        print("Inode:", info.st_ino)
        print("Тип файла:", kind)
        print("Тип и права доступа:", stat.filemode(info.st_mode))
        print("Права в восьмеричном виде:", oct(stat.S_IMODE(info.st_mode)))
        print("Размер:", info.st_size, "байт")
        print("Количество жёстких ссылок:", info.st_nlink)
        print("UID владельца:", info.st_uid)
        print("GID группы:", info.st_gid)
        print("Идентификатор устройства:", info.st_dev)
        print("Последний доступ (Unix timestamp):", info.st_atime)
        print("Последнее изменение содержимого (Unix timestamp):", info.st_mtime)
        if os.name == "posix":
            print("Изменение метаданных (Unix timestamp):", info.st_ctime)
    except OSError as error:
        print("Ошибка чтения информации о файле:", error)


if __name__ == "__main__":
    # Здесь можно указать путь к другому существующему файлу.
    selected_file = __file__
    show_filesystem_info(selected_file)
    show_file_info(selected_file)

    # Сравнение доступных файловых систем Linux без создания файлов.
    for other_path in ("/dev/shm", "/proc"):
        if os.path.exists(other_path):
            show_filesystem_info(other_path)
