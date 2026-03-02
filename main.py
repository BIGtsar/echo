# final_server.py
import asyncio
import socket
from Bio import Seq


def check_dna(sequence):
    """Проверка ДНК последовательности"""
    sequence = sequence.upper().strip()
    valid_chars = set('ACGTURYKMSWBDHVN')

    for char in sequence:
        if char not in valid_chars:
            return False, f"Недопустимый символ: {char}"

    seq = Seq.Seq(sequence)
    gc = (seq.count('G') + seq.count('C')) / len(seq) * 100

    return True, f"Валидно! GC-content: {gc:.1f}%"


async def handle_client(reader, writer):
    """Обработка клиента"""
    addr = writer.get_extra_info('peername')
    print(f"Клиент подключен: {addr}")

    writer.write("Введите ДНК последовательность (или 'exit'): ".encode())
    await writer.drain()

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            msg = data.decode('utf-8').strip()
            print(f"Получено от {addr}: {msg}")

            if msg.lower() == 'exit':
                writer.write("До свидания!\n".encode())
                await writer.drain()
                break

            valid, result = check_dna(msg)
            response = f"{result}\nВведите следующую последовательность: "
            writer.write(response.encode())
            await writer.drain()
    except:
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Клиент отключен: {addr}")


async def main():
    """Запуск сервера"""
    server = await asyncio.start_server(
        handle_client, 'localhost', 34561)

    print("ДНК-сервер запущен на порту 34561")

    async with server:
        await server.serve_forever()


# Простой клиент для тестирования
def simple_client():
    """Синхронный клиент для тестирования"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 34561))

    # Получаем приглашение
    print(client.recv(1024).decode(), end='')

    sequences = ["ATGCGAATTC", "ATGCGANTTC", "ATGCGXNTTC", "exit"]

    for seq in sequences:
        print(f"Отправка: {seq}")
        client.send(f"{seq}\n".encode())

        response = client.recv(1024).decode()
        print(response, end='')

        if seq == "exit":
            break

    client.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'client':
        simple_client()
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nСервер остановлен")
