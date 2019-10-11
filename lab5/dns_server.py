import socket
import time

from lab5.dns_struct_defines import Question, Answer, RR

db = []


def get_dns_name(dns_message, start):
    name = []
    while start <= len(dns_message):
        num = int(dns_message[start:start + 2], 16)
        if num == 0:
            print(name)
            start = start + 2
            return name, start
        elif (num & 0xC0) == 0xC0:
            pointer = int(dns_message[start + 2:start + 4], 16) * 2
            start = start + 4
            pointer_data, _ = get_dns_name(dns_message, pointer)
            return name + pointer_data, start
        name.append(bytes.fromhex(dns_message[start + 2:start + 2 + 2 * num]))
        start = start + 2 + 2 * num
    return name, start


def generate_name(name_array):
    name = b''
    for i in range(0, len(name_array) - 1):
        name += name_array[i]
        name += b'.'
    name += name_array[-1]
    return name


class dnsSolve:
    def __init__(self, dns_message):
        # self.__dict__ = {
        #     field: None
        #     for field in ('ID', 'Flags', 'QR', 'OpCode', 'AA', 'TC', 'RD', 'RA', 'Z'
        #                   , 'RCode', 'QDCOUNT', 'ANCOUNT', 'NSCOUNT', 'ARCOUNT')}
        self.ID = int(dns_message[0:4], 16)
        self.Flags = int((dns_message[4:8]), 16)
        self.QR = (self.Flags & 0x8000) >> 15
        self.OpCode = (self.Flags & 0x7800) >> 11
        self.AA = (self.Flags & 0x0400) >> 10
        self.TC = (self.Flags & 0x0200) >> 9
        self.RD = (self.Flags & 0x0100) >> 8
        self.RA = (self.Flags & 0x0080) >> 7
        self.Z = (self.Flags & 0x0070) >> 4  # Never used
        self.RCode = self.Flags & 0x000F
        self.QDCOUNT = int(dns_message[8:12], 16)
        self.ANCOUNT = int(dns_message[12:16], 16)
        self.NSCOUNT = int(dns_message[16:20], 16)
        self.ARCOUNT = int(dns_message[20:24], 16)
        self.Questions = dict()
        self.Answers = dict()
        start = 24
        for i in range(0, self.QDCOUNT):
            qname, start = get_dns_name(dns_message, start)
            qtype = int(dns_message[start:start + 4], 16)
            qclass = int(dns_message[start + 4:start + 8], 16)
            start = start + 8
            self.Questions[i] = (Question(qname, qtype, qclass))

        for i in range(0, self.ANCOUNT):
            a_name, start = get_dns_name(dns_message, start)
            a_type = int(dns_message[start:start + 4], 16)
            a_class = int(dns_message[start + 4:start + 8], 16)
            a_ttl = int(dns_message[start + 8:start + 16], 16)
            a_data_length = int(dns_message[start + 16:start + 20], 16)
            a_data = dns_message[start + 20: start + 20 + 2 * a_data_length]
            start = start + 20 + 2 * a_data_length
            self.Answers[i] = Answer(a_name, a_type, a_class, a_ttl, a_data_length, a_data)

    def handle(self):
        if self.QR == 0:
            print(time.time())
            for question in self.Questions.values():
                print(question)
                rr = RR(name=generate_name(question.QNAME), type=question.QTYPE, a_class=question.QCLASS)
                print(rr)

    def __str__(self):
        return str(self.__dict__)


if __name__ == "__main__":
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', 53))  # 监听在80端口
        # sock.listen(10)
        while True:
            message, clientAddress = sock.recvfrom(2048)
            print(message.hex())
            dns_query = message.hex()
            dns_solve = dnsSolve(dns_query)
            dns_solve.handle()
    except KeyboardInterrupt:
        exit()
