from rdt import socket

client = socket()
client.connect(("127.0.0.1", 7654))
client.send(b'test1')
data = client.recv(2048)
print(data)
client.close()
