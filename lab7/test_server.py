import threading

from rdt import socket

server = socket()
server.bind(('127.0.0.1', 7654))
# data = server.recv(4096)
# server.sendto(data,('127.0.0.1'))
while True:
    conn, client = server.accept()
    while True:
        data = conn.recv(4096)
        print(data)
        conn.send(data)
        conn.close()
        break

# class file_server(threading.Thread):
#     def __init__(self, conn, address):
#         threading.Thread.__init__(self)
#         self.conn = conn
#         self.address = address
#
#     def run(self):
#         data = self.conn.recv(4096)
#         print(data)
#         self.conn.send(data)
#         self.conn.close()
#
#
# if __name__ == "__main__":
#     try:
#         sock = socket()
#         sock.bind(('127.0.0.1', 7654))  # 监听在80端口
#         while True:
#             conn, address = sock.accept()
#             file_server(conn, address).start()
#     except KeyboardInterrupt:
#         exit()
