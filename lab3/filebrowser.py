import mimetypes
import os
import socket
import threading
from urllib import parse

err405 = [b'HTTP/1.0 405 Not Found\r\n', b'Connection: close\r\n', b'Content-Type:text/html; charset=utf-8\r\n',
          b'\r\n',
          b'<html><body>405 Not Found<body></html>\r\n', b'\r\n']

err404 = [b'HTTP/1.0 404 Not Found\r\n', b'Connection: close\r\n', b'Content-Type:text/html; charset=utf-8\r\n',
          b'\r\n',
          b'<html><body>404 Not Found<body></html>\r\n', b'\r\n']


def get_dir_html(dir_path):
    body = '<html><head><title>Index of%s</title></head><body bgcolor="white"><h1>Index of%s</h1><hr><pre>' % (
        dir_path, dir_path)
    for file in os.listdir(dir_path):
        body += '<a href="%s">%s</a><br>' % (dir_path + '/' + file, file)
    body += '</pre><hr></body></html>'
    content_length = 'Content-Length: %s\r\n' % str(len(body.encode()))
    html = [b'HTTP/1.0 200 OK\r\n', b'Connection: close\r\n', b'Content-Type:text/html; charset=utf-8\r\n',
            content_length.encode(), b'\r\n',
            body.encode(),
            b'\r\n']
    return html


def get_file_html(file_path):
    print(mimetypes.guess_type(file_path))
    file = open(file_path, 'rb')
    content_type = 'Content-Type: %s \r\n' % str(mimetypes.guess_type(file_path)[0])
    content_length = 'Content-Length: %s\r\n' % str(os.path.getsize(file_path))
    html = [b'HTTP/1.1 200 OK\r\n', b'Connection: close\r\n', content_type.encode(), content_length.encode(), b'\r\n',
            file.read(),
            b'\r\n']
    file.close()
    return html


def do_get(path):
    if os.path.isdir(path):
        res = get_dir_html(path)
    elif os.path.isfile(path):
        res = get_file_html(path)
    else:
        res = err404

    return res


class file_server(threading.Thread):
    def __init__(self, conn, address):
        threading.Thread.__init__(self)
        self.conn = conn
        self.address = address

    def run(self):
        data = self.conn.recv(2048).decode().split('\r\n')
        print(data)
        head = data[0].split(' ')
        res = err405
        if len(head) > 0:
            if head[0] == 'GET':
                file_path = '.' + head[1]
                file_path = parse.unquote(file_path)
                res = do_get(file_path)
        for line in res:
            self.conn.send(line)
        # print(res)
        self.conn.close()


if __name__ == "__main__":
    # mimetypes.add_type('video/x-msvideo', '.avi')

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 80))
        sock.listen(10)
        while True:
            conn, address = sock.accept()
            file_server(conn, address).start()
    except KeyboardInterrupt:
        exit()
