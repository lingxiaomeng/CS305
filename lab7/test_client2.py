from rdt import socket

while True:
    client = socket()
    client.connect(('127.0.0.1', 7654))
    client.send(b'')
    client.close()