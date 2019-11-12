from rdt import socket

file = open('alice.txt', 'rb')
new_file = open('recv_data.txt', 'wb+')
new_file.flush()
alice = file.read()
client = socket()
client.connect(('127.0.0.1', 7654))
client.send(alice)
data = client.recv()
new_file.write(data)
client.close()
file.close()
new_file.close()
