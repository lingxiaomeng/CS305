from socket import *

server = socket(AF_INET, SOCK_STREAM)
server.bind(('127.0.0.1', 7654))
server.listen(1)
while True:
    conn, client = server.accept()
    print(conn)
    print(client)
    while True:
        data = conn.recv(2048)
        if not data:
            break
        print(data)
        conn.send(data)
        conn.close()
        break
