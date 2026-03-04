import asyncio
from Bio import Seq


def check_dna(sequence):
    """DNA sequence validation"""
    sequence = sequence.upper().strip()
    valid_chars = set('ACGTURYKMSWBDHVN')

    for char in sequence:
        if char not in valid_chars:
            return f"Invalid character: {char}"

    seq = Seq.Seq(sequence)
    gc = (seq.count('G') + seq.count('C')) / len(seq) * 100

    return f"Valid! GC-content: {gc:.1f}%"


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")
    writer.write("Enter DNA sequence (or 'exit'): ".encode())
    await writer.drain()

    while True:
        data = await reader.read(1024)
        if not data:
            break

        msg = data.decode().strip()
        if not msg:
            continue

        print(f"Received from {addr}: {msg}")

        if msg.lower() == 'exit':
            writer.write("Goodbye!\n".encode())
            await writer.drain()
            break

        result = check_dna(msg)
        response = f"{result}\nEnter next sequence: "
        writer.write(response.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    print(f"Client disconnected: {addr}")


async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 34561)
    print("DNA server started on port 34561")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
