from rdt import socket

client = socket()
client.send(b'123456781234567812345678123')
# client.connect(("127.0.0.1", 7654))
# data = client.recv(2048)
# print(data)
client.close()
