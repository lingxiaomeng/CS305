import copy
import math
from time import time, localtime, sleep, strftime
from typing import List

from udp import UDPsocket


class packet:
    def __init__(self):
        self.rst = None
        self.head = None
        self.psh = None
        self.syn = None
        self.fin = None
        self.ack = None
        self.seq_num = None
        self.ack_num = None
        self.payload_len = None
        self.payload = None
        self.send_bytes = None
        self.checksum = -1

    def has_ack(self, ack_packet):
        if ack_packet.ack_num == self.seq_num + self.payload_len:
            return True
        else:
            return False

    def generate_send_packet(self, payload: bytes, rst: int, psh: int, syn: int, fin: int, ack: int, seq_num: int,
                             ack_num: int,
                             payload_len):
        self.rst = rst
        self.psh = psh
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.payload_len = payload_len
        self.payload = payload
        self.head = ((rst << 4) + (psh << 3) + (syn << 2) + (fin << 1) + (ack << 0))
        head_byte = self.head.to_bytes(2, byteorder='big')
        seq_byte = seq_num.to_bytes(4, byteorder='big')
        seq_ack_byte = ack_num.to_bytes(4, byteorder='big')
        payload_len_byte = payload_len.to_bytes(4, byteorder='big')
        to_be_check = head_byte + seq_byte + seq_ack_byte + payload_len_byte + payload
        self.checksum = self.cal_check_sum(to_be_check)
        self.send_bytes = head_byte + seq_byte + seq_ack_byte + payload_len_byte + self.checksum.to_bytes(2,
                                                                                                          byteorder='big') + payload

    def handle_recv_packet(self, recv_packet: bytes):
        if recv_packet is None:
            print("None packet")
            return
        self.checksum = self.cal_check_sum(recv_packet) & 0xFFFF
        self.head = (recv_packet[0] << 8) + recv_packet[1]
        self.rst = (self.head & 16) >> 4
        self.psh = (self.head & 8) >> 3
        self.syn = (self.head & 4) >> 2
        self.fin = (self.head & 2) >> 1
        self.ack = self.head & 1
        self.seq_num = (recv_packet[2] << 24) + (recv_packet[3] << 16) + (recv_packet[4] << 8) + (recv_packet[5] << 0)
        self.ack_num = (recv_packet[6] << 24) + (recv_packet[7] << 16) + (recv_packet[8] << 8) + (recv_packet[9] << 0)
        self.payload_len = (recv_packet[10] << 24) + (recv_packet[11] << 16) + (recv_packet[12] << 8) + (
                recv_packet[13] << 0)
        self.payload = recv_packet[16:]
        # print(self)

        if self.checksum != 0:
            # print("packet error:{}".format(str(self)))
            return

    @staticmethod
    def cal_check_sum(msg: bytes):
        s = 0
        for i in range(0, len(msg)):
            if i % 2 == 0:
                s += msg[i] << 8
            else:
                s += msg[i]
            s = (s & 0xFFFF) + (s >> 16)
        s = (s & 0xFFFF) + (s >> 16)
        s = (~s) & 0xFFFF
        return s

    def __str__(self):
        return 'rst = {} syn = {} ack ={}, fin = {},psh={}, seq_num ={},ack_num={},len={},data={},checksum={} '.format(
            self.rst,
            self.syn,
            self.ack,
            self.fin,
            self.psh,
            self.seq_num,
            self.ack_num,
            self.payload_len,
            self.payload,
            self.checksum)

    def __repr__(self):
        return self.__str__()


class socket(UDPsocket):
    LISTEN = 0
    SYN_RECV = 1
    SYN_SENT = 2
    CLOSED = -1
    ESTABLISHED = 3
    FIN_WAIT_1 = 4
    FIN_WAIT_2 = 5
    TIME_WAIT = 6
    CLOSING = 7
    CLOSE_WAIT = 8
    LAST_ACK = 9

    state_dict = {0: "LISTEN", 1: "SYN_RECV", 2: "SYN_SENT", 3: "ESTABLISHED", 4: "FIN_WAIT_1", 5: "FIN_WAIT_2",
                  6: "TIME_WAIT", 7: "CLOSING", 8: "CLOSE_WAIT", 9: "LAST_ACK", -1: "CLOSED"}

    def __init__(self):
        super(socket, self).__init__()
        self.setblocking(False)
        self.to_addr = None
        self.seq_num = 0
        self.ack_num = 0
        self.is_timeout = False

        self.max_payload_len = 16
        self.window_size = 4 * self.max_payload_len

        self.state = self.CLOSED
        self.sender_state = 0
        self.recv_state = 0
        self.next_seq_num = 0

        self.base = 0
        self.init_time = time()

        self.max_delay_time = 0.1
        self.last_state = 0
        self.is_server = False

    def connect(self, address):
        self.is_server = False
        self.init_time = time()
        self.state = self.LISTEN
        self.to_addr = address
        self.fsm(rst=0, syn=0, ack=0, fin=0, close=0, connect=1,
                 to_address=self.to_addr, recv_packet=None)
        while self.state != self.ESTABLISHED:
            try:
                recv = super().recvfrom(2048)
                if recv:
                    data, addr = recv
                    recv_packet = packet()
                    recv_packet.handle_recv_packet(data)
                    print(recv_packet)
                    if recv_packet.checksum == 0:
                        self.fsm(rst=recv_packet.rst, syn=recv_packet.syn, ack=recv_packet.ack, fin=recv_packet.fin,
                                 close=0, connect=1,
                                 to_address=addr, recv_packet=recv_packet)
            except BlockingIOError:
                self.fsm(rst=0, syn=0, ack=0, fin=0, close=0, connect=1,
                         to_address=self.to_addr, recv_packet=None)

            if self.state == self.CLOSED:
                print("connect timeout, Force ESTABLISHED")
                self.state = self.ESTABLISHED
        print("client connected")

    def accept(self):
        print("start accept")
        self.state = self.LISTEN
        # self.init_time = time()
        while self.state != self.ESTABLISHED:
            if self.state == self.CLOSED:
                if self.to_addr:
                    print("received message and Force connection establishment")
                    self.state = self.ESTABLISHED
                else:
                    print("accept connect failed")
                    self.state = self.LISTEN
            try:
                recv = super().recvfrom(2048)
                if recv:
                    data, addr = recv
                    recv_packet = packet()
                    recv_packet.handle_recv_packet(data)
                    if recv_packet.checksum == 0 and (
                            not self.to_addr or self.to_addr == addr):
                        self.fsm(rst=recv_packet.rst, syn=recv_packet.syn, ack=recv_packet.ack, fin=recv_packet.fin,
                                 close=0, connect=0,
                                 to_address=addr, recv_packet=recv_packet)
            except BlockingIOError:
                self.fsm(rst=0, syn=0, ack=0, fin=0, close=0, connect=0,
                         to_address=self.to_addr, recv_packet=None)
            except ConnectionResetError:
                print("ConnectionResetError")

        print("server accepted")
        return self, self.to_addr

    def close(self):
        print("start close")
        self.init_time = time()
        while self.state != self.CLOSED:
            try:
                recv = super().recvfrom(2048)
                if recv:
                    data, addr = recv
                    recv_packet = packet()
                    recv_packet.handle_recv_packet(data)
                    if recv_packet.checksum == 0:
                        self.fsm(rst=recv_packet.rst, syn=recv_packet.syn, ack=recv_packet.ack, fin=recv_packet.fin,
                                 close=1, connect=0,
                                 to_address=addr, recv_packet=recv_packet)
            except BlockingIOError:
                if not self.is_server:
                    self.fsm(rst=0, syn=0, ack=0, fin=0, close=1, connect=0,
                             to_address=self.to_addr, recv_packet=None)
                else:
                    self.fsm(rst=0, syn=0, ack=0, fin=0, close=0, connect=0,
                             to_address=self.to_addr, recv_packet=None)
            except ConnectionResetError:
                self.state = self.CLOSED

        self.to_addr = None
        self.seq_num = 0
        self.ack_num = 0
        self.is_timeout = False

        self.state = self.CLOSED
        self.sender_state = 0
        self.recv_state = 0
        self.next_seq_num = 0
        self.last_state = 0
        self.base = 0
        self.init_time = time()
        print("{} closed".format(self.to_addr))

    def recv(self, bufsize):
        print("start receive")
        expected_seq_num = self.ack_num
        recv_data = b''
        while True:
            try:
                recv = super().recvfrom(2048)
                if recv:
                    data, addr = recv
                    recv_packet = packet()
                    recv_packet.handle_recv_packet(data)
                    # print("receiver: received: " + str(recv_packet) + strftime("%Y-%m-%d %H:%M:%S",
                    #                                                            localtime()))
                    if recv_packet.checksum == 0 and addr == self.to_addr:
                        # print('recv seq num: {} expected_seq_num: {}'.format(recv_packet.seq_num, expected_seq_num))
                        if recv_packet.seq_num == expected_seq_num:
                            self.ack_num = recv_packet.seq_num + recv_packet.payload_len
                            self.seq_num = recv_packet.ack_num
                            expected_seq_num += recv_packet.payload_len
                            recv_data += recv_packet.payload
                            if recv_packet.psh:
                                break
                        ack_packet = packet()
                        ack_packet.generate_send_packet(payload=b'', rst=0, psh=0, syn=0, fin=0, ack=1,
                                                        seq_num=self.seq_num, ack_num=self.ack_num, payload_len=0)
                        self.sendto(ack_packet.send_bytes, self.to_addr)
                        # print("receiver: send: " + str(ack_packet) + strftime("%Y-%m-%d %H:%M:%S",
                        #                                                       localtime()))
            except BlockingIOError:
                pass
        print("end receive")
        return recv_data

    def send(self, data: bytes, flags: int = ...):
        print("start send")
        self.next_seq_num = self.seq_num
        packets = []
        packet_num = math.ceil(len(data) / self.max_payload_len)
        for i in range(packet_num - 1):
            packet_i = packet()
            packet_i.generate_send_packet(rst=0, ack=1, ack_num=self.ack_num, fin=0,
                                          payload_len=self.max_payload_len,
                                          seq_num=self.seq_num + i * self.max_payload_len,
                                          payload=data[i * self.max_payload_len:(i + 1) * self.max_payload_len], psh=0,
                                          syn=0)
            packets.append(packet_i)
        packet_i = packet()
        packet_i.generate_send_packet(rst=0, ack=1, ack_num=self.ack_num, fin=0,
                                      payload_len=len(data) - (packet_num - 1) * self.max_payload_len,
                                      seq_num=self.seq_num + (packet_num - 1) * self.max_payload_len,
                                      payload=data[(packet_num - 1) * self.max_payload_len:], psh=1,
                                      syn=0)
        packets.append(packet_i)
        print(packets)
        self.base = self.seq_num
        start_packet_num = 0
        cur_packet_num = 0
        while True:
            # print(self.next_seq_num)
            if self.next_seq_num < self.base + self.window_size and self.next_seq_num <= self.seq_num + (
                    packet_num - 1) * self.max_payload_len:
                self.sendto(packets[cur_packet_num].send_bytes, self.to_addr)
                # print("sender: send: " + str(packets[cur_packet_num]) + strftime("%Y-%m-%d %H:%M:%S",
                #                                                                  localtime()))
                if self.base == self.next_seq_num:
                    self.init_time = time()
                    self.is_timeout = False
                self.next_seq_num += packets[cur_packet_num].payload_len
                cur_packet_num += 1
            try:
                recv = super().recvfrom(2048)
                if recv:
                    recv_data, addr = recv
                    recv_packet = packet()
                    recv_packet.handle_recv_packet(recv_data)
                    # print("sender: received: " + str(recv_packet) + strftime("%Y-%m-%d %H:%M:%S",
                    #                                                          localtime()))
                    if recv_packet.checksum == 0:
                        ack_index = self.find_ack_index(packets, recv_packet)
                        if ack_index >= 0:
                            self.base = recv_packet.ack_num + recv_packet.payload_len
                            start_packet_num = ack_index + 1
                            if self.base == self.next_seq_num or recv_packet.ack_num == self.next_seq_num:
                                self.seq_num = self.next_seq_num
                                break
                            else:
                                self.init_time = time()
                                self.is_timeout = False
            except BlockingIOError:
                if self.base == self.next_seq_num:
                    break
                # self.is_timeout = True
            if time() - self.init_time >= self.max_delay_time:
                self.init_time = time()
                self.is_timeout = False
                # print("time out")
                for i in range(start_packet_num, cur_packet_num):
                    self.sendto(packets[i].send_bytes, self.to_addr)
                    # print("sender: send: " + str(packets[i]) + strftime("%Y-%m-%d %H:%M:%S",
                    #                                                     localtime()))

        print("end send")

    @staticmethod
    def find_ack_index(send_packets: List[packet], recv_packet: packet):
        for i in range(len(send_packets)):
            if send_packets[i].has_ack(recv_packet):
                return i
        return -1

    def fsm(self, rst, syn, ack, fin, close, connect, to_address, recv_packet):
        # print("syn: " + str(syn) + " ack: " + str(ack) + " fin: " + str(fin) + " state: " + str(
        #     self.state) + " close: " + str(close) + " connect: " + str(connect))

        packet_to_sent = None
        if time() - self.init_time > self.max_delay_time:
            self.is_timeout = True
        else:
            self.is_timeout = False

        last_state = self.state
        if self.state != self.LISTEN and self.to_addr != to_address:
            return
        if self.state == self.LISTEN:
            if syn:
                self.to_addr = to_address
                self.state = self.SYN_RECV
                packet_to_sent = packet()
                self.ack_num = recv_packet.seq_num + 1
                packet_to_sent.generate_send_packet(payload=b'', rst=0, psh=0, syn=1, ack=1, fin=0,
                                                    seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
            elif connect:
                self.state = self.SYN_SENT
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(payload=b'', rst=0, psh=0, syn=1, ack=0, fin=0,
                                                    seq_num=self.seq_num,
                                                    ack_num=self.ack_num, payload_len=0)
            elif close:
                self.state = self.CLOSED
            elif fin:
                rst_packet = packet()
                rst_packet.generate_send_packet(payload=b'', rst=1, psh=0, syn=0, ack=0, fin=0,
                                                seq_num=self.seq_num,
                                                ack_num=self.ack_num, payload_len=0)
                try:
                    self.sendto(rst_packet.send_bytes, to_address)
                except ConnectionResetError:
                    pass
        elif self.state == self.SYN_SENT:
            if close:
                self.state = self.CLOSED
            elif syn and not ack:
                packet_to_sent = packet()
                self.ack_num = recv_packet.seq_num + 1
                self.seq_num = recv_packet.ack_num + packet_to_sent.payload_len
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.state = self.SYN_RECV
            elif syn and ack:
                packet_to_sent = packet()
                self.ack_num = recv_packet.seq_num + 1
                self.seq_num = recv_packet.ack_num + recv_packet.payload_len
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.state = self.ESTABLISHED
            elif self.is_timeout:
                self.init_time = time()
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(payload=b'', rst=0, psh=0, syn=1, ack=0, fin=0,
                                                    seq_num=self.seq_num,
                                                    ack_num=self.ack_num, payload_len=0)

        elif self.state == self.SYN_RECV:
            if ack:
                self.state = self.ESTABLISHED
            if close:
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=0, fin=1, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.state = self.FIN_WAIT_1
            elif self.is_timeout:
                self.init_time = time()
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(payload=b'', rst=0, psh=0, syn=1, ack=1, fin=0,
                                                    seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)

        elif self.state == self.ESTABLISHED:
            if fin:
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)

                self.state = self.CLOSE_WAIT
            elif close:
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=1, fin=1, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)

                self.state = self.FIN_WAIT_1
        elif self.state == self.FIN_WAIT_1:
            if fin and not ack:
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)

                self.state = self.CLOSING
            elif fin and ack:
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)

                self.state = self.TIME_WAIT
            elif not fin and ack and recv_packet.seq_num == self.ack_num:
                self.state = self.FIN_WAIT_2
            elif self.is_timeout:
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=1, fin=1, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
            elif rst:
                self.state = self.CLOSED

        elif self.state == self.FIN_WAIT_2:
            if fin:
                packet_to_sent = packet()
                packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.state = self.TIME_WAIT

        elif self.state == self.CLOSING:
            if ack:
                self.state = self.TIME_WAIT
            elif self.is_timeout:
                self.state = self.TIME_WAIT

        elif self.state == self.TIME_WAIT:
            sleep(0.002)
            self.state = self.CLOSED
        elif self.state == self.CLOSE_WAIT:
            packet_to_sent = packet()
            packet_to_sent.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=0, fin=1, seq_num=self.seq_num,
                                                ack_num=self.ack_num,
                                                payload_len=0)
            self.state = self.LAST_ACK
            print(self.state_dict[self.state])
        elif self.state == self.LAST_ACK:
            if ack and not fin:
                self.state = self.CLOSED
            elif rst:
                self.state = self.CLOSED
            elif self.is_timeout:
                self.init_time = time()
                fin_packet = packet()
                fin_packet.generate_send_packet(b'', rst=0, psh=0, syn=0, ack=0, fin=1, seq_num=self.seq_num,
                                                ack_num=self.ack_num,
                                                payload_len=0)
                try:
                    self.sendto(fin_packet.send_bytes, self.to_addr)
                except ConnectionResetError:
                    self.state = self.CLOSED
        # if recv_packet:
        # print("fsm: received: " + str(recv_packet) + " " + strftime("%Y-%m-%d %H:%M:%S",
        #                                                             localtime()))
        if packet_to_sent:
            # print("fsm: send: " + str(packet_to_sent) + " " + strftime("%Y-%m-%d %H:%M:%S",
            #                                                            localtime()))
            self.sendto(packet_to_sent.send_bytes, self.to_addr)

        if self.state != last_state:
            self.init_time = time()
            print("FSM state:" + self.state_dict[self.state])
