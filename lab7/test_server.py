from rdt import socket

try:
    server = socket()
    server.bind(('127.0.0.1', 7654))
    while True:
        conn, client = server.accept()
        conn.close()
        break
except ConnectionResetError:
    print("error")
