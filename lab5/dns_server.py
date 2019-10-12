import socket
import time
import struct
from lab5.dns_struct_defines import Question, Answer, RR, RR_type


def get_dns_name(dns_message, start):
    end = start
    name = []
    name_original = ''
    while end <= len(dns_message):
        num = int(dns_message[end:end + 2], 16)
        if num == 0:
            end = end + 2
            name_original = dns_message[start:end]
            return name, end, name_original
        elif (num & 0xC0) == 0xC0:
            # print("has pointer")
            pointer = int(dns_message[end + 2:end + 4], 16) * 2
            name_original = dns_message[start:end]
            end = end + 4
            pointer_data, _, pointer_data_original = get_dns_name(dns_message, pointer)
            return name + pointer_data, end, name_original + pointer_data_original
        name.append(bytes.fromhex(dns_message[end + 2:end + 2 + 2 * num]))
        end = end + 2 + 2 * num
    return name, end, name_original


# def generate_name(name_array):
#     name = b''
#     for i in range(0, len(name_array) - 1):
#         name += name_array[i]
#         name += b'.'
#     name += name_array[-1]
#     return name


class dnsSolve:
    def __init__(self, dns_message):
        self.DNS_message = dns_message
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
        self.RRs = dict()
        start = 24
        for i in range(0, self.QDCOUNT):
            qname, end, qname_origin = get_dns_name(dns_message, start)
            qtype = int(dns_message[end:end + 4], 16)
            qclass = int(dns_message[end + 4:end + 8], 16)
            start = end + 8
            self.Questions[i] = (Question(qname, qtype, qclass, qname_origin))

        for i in range(0, self.ANCOUNT + self.NSCOUNT + self.ARCOUNT):
            a_name, end, a_name_original = get_dns_name(dns_message, start)
            a_type = int(dns_message[end:end + 4], 16)
            a_class = int(dns_message[end + 4:end + 8], 16)
            a_ttl = int(dns_message[end + 8:end + 16], 16)
            a_data_length = int(dns_message[end + 16:end + 20], 16)
            if a_type == RR_type.CNAME:
                _, _, a_data = get_dns_name(dns_message, end + 20)
            else:
                a_data = dns_message[end + 20: end + 20 + 2 * a_data_length]
            start = end + 20 + 2 * a_data_length
            self.RRs[i] = Answer(a_name, a_type, a_class, a_ttl, a_data_length, a_data, a_name_original)

    @staticmethod
    def generate_answer(rr):
        tle = (rr.due_date - time.time()) <= 0
        if tle:
            db.remove(rr)
            print("TLE")
            return b''
        else:
            answer = bytes.fromhex(rr.name) + struct.pack('>H', rr.a_type) + struct.pack('>H',
                                                                                         rr.a_class) + struct.pack(
                '>L', int(rr.due_date - time.time())) + struct.pack('>H', rr.data_length) + bytes.fromhex(rr.data)
            return answer

    def find_record(self, rr):
        answer_num = 0
        finial_answer = b''
        for old_rr in db:
            if rr.__eq__(old_rr):
                answer = self.generate_answer(old_rr)
                if old_rr.a_type == RR_type.CNAME:
                    cname_record = RR(name=old_rr.data, a_type=0, a_class=0)
                    a_record, num = self.find_record(cname_record)
                    if num > 0 and len(answer) > 0:
                        answer_num = answer_num + num + 1
                        finial_answer += a_record
                        finial_answer += answer
                elif old_rr.a_type == RR_type.A or RR_type.AAAA or RR_type.TXT or RR_type.NS or RR_type.MX:
                    finial_answer += answer
                    answer_num += 1
        return finial_answer, answer_num

    def generate_header(self, qdcount):
        flags = 0b1000000110000000
        header = struct.pack('>H', self.ID) + struct.pack('>H', flags) + struct.pack('>H', 0) + struct.pack(
            '>H', qdcount) + struct.pack('>H', 0) + struct.pack('>H', 0)
        return header

    def handle(self, address):
        # for rr in db:
        #     print(rr)
        if self.QR == 0:
            for question in self.Questions.values():
                rr = RR(name=question.QNAME_original, a_type=question.QTYPE, a_class=question.QCLASS)
                answer, qdcount = self.find_record(rr)
                if qdcount > 0:
                    head = self.generate_header(qdcount)
                    severSocket.sendto(head + answer, address)
                    print("find")
                else:
                    print("not find")
                    clientSocket.sendto(bytes.fromhex(self.DNS_message), ('172.18.1.92', 53))
                    foreign_name_server_response, foreign_name_server_address = clientSocket.recvfrom(2048)
                    severSocket.sendto(foreign_name_server_response, address)
                    dns_answer = dnsSolve(foreign_name_server_response.hex())
                    dns_answer.handle(foreign_name_server_address)
                # print(response)
        elif self.QR == 1:
            for answer in self.RRs.values():
                # print(answer)
                rr = RR(name=answer.A_name_original, a_type=answer.A_type, a_class=answer.A_class,
                        data=answer.A_data, due_date=time.time() + answer.A_ttl)
                db.append(rr)

    def __str__(self):
        return str(self.__dict__)


if __name__ == "__main__":
    db = []
    try:
        severSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        severSocket.bind(('127.0.0.1', 53))  # 监听在53端口
        while True:
            message, clientAddress = severSocket.recvfrom(2048)
            dns_solve = dnsSolve(message.hex())
            dns_solve.handle(clientAddress)
    except KeyboardInterrupt:
        exit()
