from rdt import socket

server = socket()
server.bind(('127.0.0.1', 7654))
while True:
    conn, client = server.accept()
    while True:
        data = conn.recv(2048)
        conn.send(data)
        conn.close()
        break
