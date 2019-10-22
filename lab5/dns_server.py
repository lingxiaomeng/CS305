import socket
import struct
import time
from dns_struct_defines import Question, Answer, RR, RR_type

foreign_DNS_address = ('172.18.1.92', 53)


def get_dns_name(dns_message, start):  # 解包NAME 结尾为0x00 返回 结尾为指针 继续递归寻找
    end = start
    name = []
    name_original = ''
    while end <= len(dns_message):
        num = int(dns_message[end:end + 2], 16)
        if num == 0:
            end = end + 2
            name_original = dns_message[start:end]
            return name, end, name_original
        elif (num & 0xC0) == 0xC0:  # 最高位为11 时为指针
            pointer = (int(dns_message[end + 2:end + 4], 16) + num & 0x3F) * 2
            name_original = dns_message[start:end]
            end = end + 4
            pointer_data, _, pointer_data_original = get_dns_name(dns_message, pointer)
            return name + pointer_data, end, name_original + pointer_data_original
        name.append(bytes.fromhex(dns_message[end + 2:end + 2 + 2 * num]))
        end = end + 2 + 2 * num
    return name, end, name_original  # name 为解析过的数组(便于debug) name_original为原始编码


def generate_answer(rr):  # 生成一条回答
    ttl = int(rr.DUE_DATE - time.time())
    if ttl < 10:  # 令最短TTL为10
        cache.remove(rr)
        print("TLE")
        return b''
    else:
        answer = bytes.fromhex(rr.NAME_Original) + struct.pack('>H', rr.TYPE) + struct.pack('>H',
                                                                                            rr.CLASS) + struct.pack(
            '>L', ttl) + struct.pack('>H', rr.DATA_LENGTH) + bytes.fromhex(rr.DATA)
        return answer


def find_record(rr):  # 在cache中寻找记录
    answer_num = 0  # 记录RR数目
    finial_answer = b''
    for old_rr in cache:
        if rr.__eq__(old_rr):
            answer = generate_answer(old_rr)  # 生成一条回复
            if len(answer) > 0:
                if old_rr.TYPE == RR_type.CNAME:  # 如果type为CANME 继续递归寻找CNAME对应的A记录
                    cname_record = RR(name_original=old_rr.DATA, a_type=rr.TYPE, a_class=rr.CLASS, name=[])
                    a_record, num = find_record(cname_record)
                    if num > 0 or rr.TYPE == RR_type.CNAME:
                        answer_num = answer_num + num + 1
                        finial_answer += a_record
                        finial_answer += answer
                elif old_rr.TYPE == RR_type.A or RR_type.AAAA or RR_type.TXT or RR_type.NS or RR_type.MX:
                    finial_answer += answer
                    answer_num += 1
    return finial_answer, answer_num


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
        self.Z = (self.Flags & 0x0070) >> 4
        self.RCode = self.Flags & 0x000F
        self.QDCOUNT = int(dns_message[8:12], 16)
        self.ANCOUNT = int(dns_message[12:16], 16)
        self.NSCOUNT = int(dns_message[16:20], 16)
        self.ARCOUNT = int(dns_message[20:24], 16)  # 解析报头
        self.Questions = dict()  # question
        self.RRs = dict()  # RR记录
        start = 24
        for i in range(0, self.QDCOUNT):  # 解包Question
            qname, end, qname_origin = get_dns_name(dns_message, start)
            qtype = int(dns_message[end:end + 4], 16)
            qclass = int(dns_message[end + 4:end + 8], 16)
            start = end + 8
            self.Questions[i] = (Question(qname, qtype, qclass, qname_origin))
        self.QUESTIONS = dns_message[24:start]

        for i in range(0, self.ANCOUNT + self.NSCOUNT + self.ARCOUNT):  # 解包RR
            a_name, end, a_name_original = get_dns_name(dns_message, start)
            a_type = int(dns_message[end:end + 4], 16)
            a_class = int(dns_message[end + 4:end + 8], 16)
            a_ttl = int(dns_message[end + 8:end + 16], 16)
            a_data_length = int(dns_message[end + 16:end + 20], 16)
            if a_type == RR_type.CNAME or a_type == RR_type.NS:  # 如果为CNAME或NS解出其完整DATA
                _, _, a_data = get_dns_name(dns_message, end + 20)
            else:
                a_data = dns_message[end + 20: end + 20 + 2 * a_data_length]
            start = end + 20 + 2 * a_data_length
            self.RRs[i] = Answer(a_name=a_name, a_name_original=a_name_original, a_class=a_class, a_ttl=a_ttl,
                                 a_data_length=0, a_data=a_data, a_type=a_type)

    def generate_header(self, ancount):  # 生成返回Header
        flags = 0b1000000110000000  # FLAGS
        header = struct.pack('>H', self.ID) + struct.pack('>H', flags) + struct.pack('>H', self.QDCOUNT) + struct.pack(
            '>H', ancount) + struct.pack('>H', 0) + struct.pack('>H', 0) + bytes.fromhex(self.QUESTIONS)
        return header

    def handle(self, address):  # 处理事件
        if self.QR == 0:  # 如果是查询报文
            for question in self.Questions.values():  # 处理Question列表
                answer, qdcount = find_record(question)
                if qdcount > 0:  # cache中有记录
                    head = self.generate_header(qdcount)
                    severSocket.sendto(head + answer, address)  # 返回给客户端
                    print("find in cache")
                else:  # 向远程服务器查询
                    print("not find")
                    clientSocket.sendto(bytes.fromhex(self.DNS_message), foreign_DNS_address)  # 将报文直接转发
                    foreign_name_server_response, foreign_name_server_address = clientSocket.recvfrom(2048)  # 等待回复
                    severSocket.sendto(foreign_name_server_response, address)  # 将相映报文发回请求客户端
                    dns_answer = dnsSolve(foreign_name_server_response.hex())
                    dns_answer.handle(foreign_name_server_address)  # 保存记录
        elif self.QR == 1:
            for answer in self.RRs.values():
                rr = RR(name=answer.NAME, a_type=answer.TYPE, a_class=answer.CLASS,
                        data=answer.DATA, due_date=time.time() + answer.A_ttl, name_original=answer.NAME_Original)
                for old_rr in cache:
                    if old_rr.NAME_Original == rr.NAME_Original and rr.DATA == old_rr.DATA:
                        cache.remove(old_rr)  # 将冲突记录删除
                cache.append(rr)

    def __str__(self):
        return str(self.__dict__)


if __name__ == "__main__":
    cache = []
    try:
        severSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        severSocket.bind(('127.0.0.1', 53))  # 监听端口53
        while True:
            message, clientAddress = severSocket.recvfrom(2048)
            dns_solve = dnsSolve(message.hex())
            dns_solve.handle(clientAddress)
    except KeyboardInterrupt:
        exit()
