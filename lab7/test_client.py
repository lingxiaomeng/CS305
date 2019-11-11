from rdt import socket

num = 0

file = open('alice.txt', 'rb')
new_file = open('recv_data.txt', 'wb+')
new_file.flush()
alice = file.read()
# while True:
client = socket()
client.connect(('127.0.0.1', 7654))
client.send(alice)
data = client.recv(4096)
# print(data)
new_file.write(data)
client.close()
num += 1
print(num)

file.close()
new_file.close()
