from socket import *

client = socket(AF_INET, SOCK_STREAM)
client.bind(('127.0.0.1', 8888))
client.connect(("127.0.0.1", 7654))
client.send(b'123456')
data = client.recvfrom(2048)
print(data)
client.close()
