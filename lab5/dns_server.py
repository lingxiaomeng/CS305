import socket

from lab5.dns_struct_defines import Question


def get_dns_name(dns_message, start):
    name = []
    while start <= len(dns_message):
        num = int(dns_message[start:start + 2], 16)
        if num == 0:
            start = start + 2
            return name, start, False
        elif (num & 0xC) == 0xC:
            start = start + 2
            return name, start, True
        name.append(bytes.fromhex(dns_message[start + 2:start + 2 + 2 * num]))
        start = start + 2 + 2 * num


class dnsSolve:
    def __init__(self, dns_message):
        # self.__dict__ = {
        #     field: None
        #     for field in ('ID', 'Flags', 'QR', 'OpCode', 'AA', 'TC', 'RD', 'RA', 'Z'
        #                   , 'RCode', 'QDCOUNT', 'ANCOUNT', 'NSCOUNT', 'ARCOUNT')}
        self.ID = int(dns_message[0:4])
        self.Flags = int((dns_message[4:8]), 16)
        self.QR = (self.Flags & 0x8000)
        self.OpCode = (self.Flags & 0x7800) >> 11
        self.AA = (self.Flags & 0x0400)
        self.TC = (self.Flags & 0x0200)
        self.RD = (self.Flags & 0x0100)
        self.RA = (self.Flags & 0x0080)
        self.Z = (self.Flags & 0x0070) >> 4  # Never used
        self.RCode = self.Flags & 0x000F
        self.QDCOUNT = int(dns_message[8:12], 16)
        self.ANCOUNT = int(dns_message[12:16], 16)
        self.NSCOUNT = int(dns_message[16:20], 16)
        self.ARCOUNT = int(dns_message[20:24], 16)
        self.Questions = dict()
        start = 24
        for i in range(0, self.QDCOUNT):
            qname, start, _ = get_dns_name(dns_message, start)
            qtype = int(dns_message[start:start + 2], 16)
            qclass = int(dns_message[start + 2:start + 4], 16)
            self.Questions[i] = (Question(qname, qtype, qclass))
        qname = []
        while i < self.ANCOUNT:
            num = int(dns_message[start:start + 2], 16)
            if num == 0:
                qtype = int(dns_message[start + 2:start + 4], 16)
                qclass = int(dns_message[start + 4:start + 6], 16)
                self.Questions[i] = (Question(qname, qtype, qclass))
                start = start + 6
                i = i + 1
            qname.append(bytes.fromhex(dns_message[start + 2:start + 2 + 2 * num]))
            start = start + 2 + 2 * num

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
            print(dns_solve)
    except KeyboardInterrupt:
        exit()
