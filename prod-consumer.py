import mmap
import multiprocessing
import time

BUFFER_SIZE = 1024


def producer(shared_memory):
    """Производитель записывает строку в общую память."""
    message = "Хелоу от производителя."

    # Преобразуем строку в байты
    data = message.encode("utf-8")

    # Сначала записываем длину сообщения
    shared_memory.seek(0)
    shared_memory.write(len(data).to_bytes(4, byteorder="big"))

    # Затем записываем само сообщение
    shared_memory.write(data)

    print("Производитель отправил:", message)
    print("\n")


def consumer(shared_memory):
    """Потребитель читает строку из общей памяти."""
    # Небольшая задержка чтобы производитель успел записать данные
    time.sleep(1)

    # Читаем длину сообщения
    shared_memory.seek(0)
    length = int.from_bytes(
        shared_memory.read(4),
        byteorder="big"
    )

    # Читаем сообщение
    data = shared_memory.read(length)
    message = data.decode("utf-8")

    print("Я потребитель и я получил вот что:", message)


if __name__ == "__main__":
    # Создаём буфер общей памяти
    shared_memory = mmap.mmap(-1, BUFFER_SIZE)

    # Создаём отдельные процессы
    producer_process = multiprocessing.Process(
        target=producer,
        args=(shared_memory,)
    )

    consumer_process = multiprocessing.Process(
        target=consumer,
        args=(shared_memory,)
    )

    # Запускаем процессы
    producer_process.start()
    consumer_process.start()

    # Ждём завершения процессов
    producer_process.join()
    consumer_process.join()

    # Освобождаем общую память
    shared_memory.close()

    print("Работа программы завершена.")