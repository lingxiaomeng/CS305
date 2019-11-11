from socket import *

client = socket(AF_INET, SOCK_STREAM)
client.connect(("127.0.0.1", 7777))
client.send(b'123456')
data = client.recvfrom(2048)
print(client)
print(data)
client.close()
