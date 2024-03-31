import socket
import sys


def work(host: str, port: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(2)
    conn, addr = server.accept()

    while True:
        data = conn.recv(1024).decode()

        if not data:
            break

        print("from connected user: " + str(data))
        conn.send(' -> '.encode())

    conn.close()


if __name__ == '__main__':
    try:
        (_, host, port) = sys.argv
        print(f"Worker starts: {host}:{port}")
        work(host, int(port))
    except ValueError:
        exit('!')
    except KeyboardInterrupt:
        exit('\n\rWorker exit')
