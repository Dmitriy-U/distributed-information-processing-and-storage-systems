import time
import socket
import sys

from helpers import get_prime_numbers


def work():
    client_socket = socket.socket()
    client_socket.connect(('127.0.0.1', 8888))

    client_socket.send('123'.encode())
    data = client_socket.recv(1024).decode()

    print('Received from server: ' + data)

    client_socket.close()


if __name__ == '__main__':
    try:
        (_, prime_search_range_start_number, prime_search_range_end_number) = sys.argv
        range_start = int(prime_search_range_start_number)
        range_end = int(prime_search_range_end_number)
        print("Program starts", f"range start: {range_start}", f"range start: {range_end}", sep="\n\r")
        time_start = time.time()
        get_prime_numbers(range_start, range_end)
        time_end = time.time()
        print(f'time: {time_end - time_start}c')
        work()
    except ValueError:
        exit('!')
    except KeyboardInterrupt:
        exit('\n\rProgram exit')
