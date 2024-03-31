import socket
import sys


def work(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                print('data', data.decode("utf-8"))
                if not data:
                    break
                conn.sendall(data)


if __name__ == '__main__':
    try:
        (_, host, port) = sys.argv
        print(host, port)
        work(host, int(port))
    except ValueError:
        exit('!')
