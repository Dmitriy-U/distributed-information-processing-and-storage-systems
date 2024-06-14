import socket

s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 9001))
message = s.recvfrom(1024)
print(message)
