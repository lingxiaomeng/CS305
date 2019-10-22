import mimetypes
import os
import socket
import threading
import time

from urllib import parse

import chardet

err405 = [b'HTTP/1.0 405 Method Not Allowed\r\n', b'Connection: close\r\n',
          b'Content-Type:text/html; charset=utf-8\r\n',
          b'\r\n',
          b'<html><body>405 Method Not Allowed<body></html>\r\n', b'\r\n']

err404 = [b'HTTP/1.0 404 Not Found\r\n', b'Connection: close\r\n', b'Content-Type:text/html; charset=utf-8\r\n',
          b'\r\n',
          b'<html><body>404 Not Found<body></html>\r\n', b'\r\n']

server_path = '127.0.0.1'
server_port = 8080


def get_parent_dir(cur_dir):
    parent_dir = cur_dir[:cur_dir.rfind('/')]
    return parent_dir


def get_simplest_dir(cur_dir):
    str_list = cur_dir.split('/')
    new_list = list()
    for substr in str_list:
        if substr != '':
            new_list.append(substr)
    return '/' + '/'.join(new_list)


class file_server(threading.Thread):
    def __init__(self, conn, address):
        threading.Thread.__init__(self)
        self.cookie = None
        self.conn = conn
        self.address = address
        self.range_start = 0
        self.range_end = 0
        self.response_range = False
        self.minsize = 10485760
        self.referer = None

    def has_range(self, header):
        for data in header:
            if 'Range' in data:
                byte_range = data[13:].split('-')
                self.range_start = int(byte_range[0])
                self.range_end = 0 if byte_range[1] == '' else int(byte_range[1])
                # print('{} {}'.format(self.range_start, self.range_end))
                return True
        return False

    def set_cookie(self, header):
        for data in header:
            if 'Cookie' in data:
                cookie = data[8:].split('=')[1]
                self.cookie = cookie

    def set_referer(self, header):
        for data in header:
            if 'Referer' in data:
                cookie = data[9:]
                self.referer = cookie

    def get_dir_html(self, dir_path):
        cookie_state[self.cookie] = get_simplest_dir(dir_path[1:])
        body = '<html><head><title>Index of %s</title></head><body bgcolor="white"><h1>Index of %s</h1><hr><pre>' % (
            dir_path, dir_path)
        body += '<a href="{}">../</a><br>'.format(get_simplest_dir(get_parent_dir(dir_path[1:])))
        for file in os.listdir(dir_path):
            body += '<a href="%s">%s</a><br>' % (get_simplest_dir(dir_path[1:] + '/' + file), file)
        body += '</pre><hr></body></html>'
        content_length = 'Content-Length: %s; charset=utf-8\r\n' % str(len(body.encode()))
        set_cookie = 'Set-Cookie: ID={}\r\n'.format(self.cookie)
        html = [b'HTTP/1.0 200 OK\r\n', b'Connection: close\r\n', b'Content-Type:text/html; charset=utf-8\r\n',
                content_length.encode(), set_cookie.encode(), b'\r\n',
                body.encode(),
                b'\r\n']
        return html

    def get_file_html(self, file_path):
        file_type = str(mimetypes.guess_type(file_path)[0])  # 获取文件content-type
        file = open(file_path, 'rb')
        data = file.read()
        # print(file_type)
        if 'text' in file_type:
            text_type = chardet.detect(data)['encoding']  # 判断文本文档的编码
            content_type = 'Content-Type: %s; charset=%s\r\n' % (file_type, text_type)
        else:
            content_type = 'Content-Type: %s\r\n' % file_type
        if self.response_range:
            file_size = os.path.getsize(file_path)
            if self.range_start >= file_size:
                self.range_start = 0
            if self.range_end == 0 or self.range_end > file_size:
                self.range_end = file_size - 1
            content_length = 'Content-Length: %d\r\n' % (self.range_end - self.range_start)
            content_range = 'Content-range: bytes %d-%d/%d\r\n' % (self.range_start, self.range_end, file_size)
            html = [b'HTTP/1.0 206 Partial content\r\n', b'Connection: close\r\n', b'Accept-Ranges: bytes\r\n',
                    content_type.encode(),
                    content_length.encode(), content_range.encode(), b'\r\n',
                    data[self.range_start:self.range_end + 1],
                    b'\r\n']
        else:
            content_length = 'Content-Length: %d\r\n' % (os.path.getsize(file_path))
            html = [b'HTTP/1.0 200 OK\r\n', b'Connection: close\r\n', b'Accept-Ranges: bytes\r\n',
                    content_type.encode(),
                    content_length.encode(), b'\r\n',
                    data,
                    b'\r\n']
        file.close()
        return html

    def do_get(self, path):
        if self.cookie:
            cookie_path = cookie_state.get(self.cookie)
            if path == './' and cookie_path and cookie_path != '/' and (
                    not self.referer or self.referer == 'http://{}:{}/'.format(server_path, server_port)):
                res = [b'HTTP/1.0 302 Found\r\n', b'Connection: close\r\n',
                       ('Location: http://%s:%d%s\r\n' % (
                           server_path, server_port, cookie_state[self.cookie])).encode(),
                       b'Content-Type:text/html; charset=utf-8\r\n',
                       b'\r\n',
                       b'<html><body>405 Method Not Allowed<body></html>\r\n', b'\r\n']
                return res
        else:
            self.cookie = str(int(time.time()))

        if os.path.isdir(path):
            res = self.get_dir_html(path)
        elif os.path.isfile(path):
            res = self.get_file_html(path)
        else:
            res = err404
        return res

    def run(self):
        data = self.conn.recv(2048).decode().split('\r\n')
        print(str(self.address) + ":" + str(data))
        self.response_range = self.has_range(data)
        self.set_cookie(data)
        self.set_referer(data)
        head = data[0].split(' ')
        res = err405  # 默认返回405
        if len(head) > 0:
            if head[0] == 'GET':
                file_path = '.' + head[1]
                file_path = parse.unquote(file_path)  # 解析中文字符
                res = self.do_get(file_path)
        try:
            for line in res:
                self.conn.send(line)
        except ConnectionAbortedError:
            print(str(self.address) + ":ConnectionAbortedError,远程主机强迫关闭了一个现有的连接")
        except ConnectionResetError:
            print(str(self.address) + ":ConnectionResetError,远程主机强迫关闭了一个现有的连接")
        except BrokenPipeError:
            print(str(self.address) + ":[Errno 32] Broken pipe")
        self.conn.close()
        print(str(self.address) + ":closed")


if __name__ == "__main__":
    try:
        cookie_state = dict()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((server_path, 8080))  # 监听在8080端口
        sock.listen(10)
        while True:
            conn, address = sock.accept()
            file_server(conn, address).start()
    except KeyboardInterrupt:
        exit()
