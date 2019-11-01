from rdt import socket

client = socket()
client.connect(("127.0.0.1", 7654))

client.send(b'123456781234567812345678123')
data = client.recv(4096)
print(data)
client.close()
