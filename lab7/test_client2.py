from rdt import socket

client = socket()
client.connect(('127.0.0.1', 7654))
client.send(b'hello world test text 123456789 123456789 123456789 123456789 123456789 123456789')
data = client.recv(4096)
print(data)
client.close()