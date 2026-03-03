# final_server.py
import asyncio
import socket
from Bio import Seq


def check_dna(sequence):
    """DNA sequence validation"""
    sequence = sequence.upper().strip()
    valid_chars = set('ACGTURYKMSWBDHVN')

    for char in sequence:
        if char not in valid_chars:
            return False, f"Invalid character: {char}"

    seq = Seq.Seq(sequence)
    gc = (seq.count('G') + seq.count('C')) / len(seq) * 100

    return True, f"Valid! GC-content: {gc:.1f}%"


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")

    writer.write("Enter DNA sequence (or 'exit'): ".encode())
    await writer.drain()

    buffer = ""  # buffer for accumulating characters

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            # Add received data to buffer
            buffer += data.decode('utf-8')

            # If there is a newline, process
            if '\n' in buffer or '\r' in buffer:
                # Split by lines
                lines = buffer.replace('\r', '\n').split('\n')
                # Last part may be incomplete
                buffer = lines[-1]

                # Process all complete lines
                for msg in lines[:-1]:
                    msg = msg.strip()
                    if msg:
                        print(f"Received from {addr}: {msg}")

                        if msg.lower() == 'exit':
                            writer.write("Goodbye!\n".encode())
                            await writer.drain()
                            break

                        valid, result = check_dna(msg)
                        response = f"{result}\nEnter next sequence: "
                        writer.write(response.encode())
                        await writer.drain()
    except:
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Client disconnected: {addr}")


async def main():
    """Server startup"""
    server = await asyncio.start_server(
        handle_client, 'localhost', 34561)

    print("DNA server started on port 34561")

    async with server:
        await server.serve_forever()


# Simple client for testing
def simple_client():
    """Synchronous client for testing"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 34561))

    # Get greeting
    print(client.recv(1024).decode(), end='')

    sequences = ["ATGCGAATTC", "ATGCGANTTC", "ATGCGXNTTC", "exit"]

    for seq in sequences:
        print(f"Sending: {seq}")
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
            print("\nServer stopped")