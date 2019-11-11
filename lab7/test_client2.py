from rdt import socket

for i in range(50):
    client = socket()
    client.connect(('127.0.0.1', 7654))
    client.send(b'1')
    # data = client.recv()
    # print(data)
    client.close()
