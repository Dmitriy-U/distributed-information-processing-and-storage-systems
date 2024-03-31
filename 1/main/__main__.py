import socket
import sys


def work(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 8888))
        while True:
            data = s.recv(1024)
            s.send("123".encode())


if __name__ == '__main__':
    try:
        (_, host, port) = sys.argv
        print(host, port)
        work(host, int(port))
    except ValueError:
        exit('!')
