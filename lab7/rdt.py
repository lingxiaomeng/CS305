import math
from time import sleep, time
from udp import UDPsocket


class packet:
    def __init__(self):
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
        self.checksum = 0

    def generate_send_packet(self, payload: bytes, psh: int, syn: int, fin: int, ack: int, seq_num: int, ack_num: int,
                             payload_len):
        self.psh = psh
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.payload_len = payload_len
        self.payload = payload
        self.head = ((psh << 3) + (syn << 2) + (fin << 1) + (ack << 0))
        head_byte = self.head.to_bytes(2, byteorder='big')
        seq_byte = seq_num.to_bytes(4, byteorder='big')
        seq_ack_byte = ack_num.to_bytes(4, byteorder='big')
        payload_len_byte = payload_len.to_bytes(4, byteorder='big')
        to_be_check = head_byte + seq_byte + seq_ack_byte + payload_len_byte + payload
        checksum = self.cal_check_sum(to_be_check)
        self.send_bytes = head_byte + seq_byte + seq_ack_byte + payload_len_byte + checksum.to_bytes(2,
                                                                                                     byteorder='big') + payload

    def handle_recv_packet(self, recv_packet: bytes):
        self.checksum = self.cal_check_sum(recv_packet) & 0xFFFF
        if self.checksum != 0:
            print("packet error")
            return
        self.head = (recv_packet[0] << 8) + recv_packet[1]
        self.psh = (self.head & 8) >> 3
        self.syn = (self.head & 4) >> 2
        self.fin = (self.head & 2) >> 1
        self.ack = self.head & 1
        self.seq_num = (recv_packet[2] << 24) + (recv_packet[3] << 16) + (recv_packet[4] << 8) + (recv_packet[5] << 0)
        self.ack_num = (recv_packet[6] << 24) + (recv_packet[7] << 16) + (recv_packet[8] << 8) + (recv_packet[9] << 0)
        self.payload_len = (recv_packet[10] << 24) + (recv_packet[11] << 16) + (recv_packet[12] << 8) + (
                recv_packet[13] << 0)
        self.payload = recv_packet[16:]
        print(self)

    @staticmethod
    def cal_check_sum(msg: bytes):
        s = 0
        for i in range(0, len(msg), 2):
            if (i + 1) < len(msg):
                s += (msg[i] << 8) + (msg[i + 1])
            elif (i + 1) == len(msg):
                s += msg[i]
            s = s + (s >> 16)
        s = ~s & 0xFFFF
        return s

    def __str__(self):
        return str(self.__dict__)

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

    def __init__(self):
        super(socket, self).__init__()
        self.setblocking(False)
        self.to_addr = None
        self.seq_num = 0
        self.ack_num = 0

        self.max_payload_len = 8
        self.window_size = 4 * self.max_payload_len

        self.state = self.CLOSED
        self.sender_state = 0
        self.recv_state = 0

        self.init_time = time()

    def connect(self, address):
        self.state = self.LISTEN
        self.to_addr = address
        self.fsm(syn=0, ack=0, fin=0, close=0, connect=1,
                 to_address=self.to_addr)
        while self.state != self.ESTABLISHED:
            try:
                data, addr = super().recvfrom(2048)
                recv_packet = packet()
                recv_packet.handle_recv_packet(data)
                if recv_packet.checksum == 0:
                    self.fsm(syn=recv_packet.syn, ack=recv_packet.ack, fin=recv_packet.fin, close=0, connect=1,
                             to_address=addr)
            except BlockingIOError:
                self.fsm(syn=0, ack=0, fin=0, close=0, connect=1,
                         to_address=self.to_addr)
        print("client connected")

    def accept(self):
        self.state = self.LISTEN
        while self.state != self.ESTABLISHED:
            try:
                data, addr = super().recvfrom(2048)
                recv_packet = packet()
                recv_packet.handle_recv_packet(data)
                if recv_packet.checksum == 0:
                    self.fsm(syn=recv_packet.syn, ack=recv_packet.ack, fin=recv_packet.fin, close=0, connect=0,
                             to_address=addr)
            except BlockingIOError:
                self.fsm(syn=0, ack=0, fin=0, close=0, connect=0,
                         to_address=self.to_addr)

        print("server accepted")
        return self, self.to_addr

    def close(self):
        print("start close")
        while self.state != self.CLOSED:
            try:
                data, addr = super().recvfrom(2048)
                recv_packet = packet()
                recv_packet.handle_recv_packet(data)
                if recv_packet.checksum == 0:
                    self.fsm(syn=recv_packet.syn, ack=recv_packet.ack, fin=recv_packet.fin, close=1, connect=0,
                             to_address=addr)
            except BlockingIOError:
                self.fsm(syn=0, ack=0, fin=0, close=1, connect=0,
                         to_address=self.to_addr)
        print("closed")

    def recv(self, bufsize):
        try:
            data, addr = super().recvfrom(2048)
            return data
        except BlockingIOError:
            pass

    def send(self, data: bytes, flags: int = ...):
        packets = []
        packet_num = math.ceil(len(data) / self.max_payload_len)
        for i in range(packet_num - 1):
            packet_i = packet()
            packet_i.generate_send_packet(ack=1, ack_num=self.ack_num, fin=0,
                                          payload_len=self.max_payload_len,
                                          seq_num=self.seq_num + i * self.max_payload_len,
                                          payload=data[i * self.max_payload_len:(i + 1) * self.max_payload_len], psh=0,
                                          syn=0)
            packets.append(packet_i)
        packet_i = packet()
        packet_i.generate_send_packet(ack=1, ack_num=self.ack_num, fin=0,
                                      payload_len=len(data) - (packet_num - 1) * self.max_payload_len,
                                      seq_num=self.seq_num + (packet_num - 1) * self.max_payload_len,
                                      payload=data[(packet_num - 1) * self.max_payload_len:], psh=1,
                                      syn=0)
        packets.append(packet_i)
        print(packets)
        super().sendto(data, self.to_addr)
        pass

    def send_fsm(self, push, syn, ack, fin):

        pass

    def fsm(self, syn, ack, fin, close, connect, to_address):
        # print("syn: " + str(syn) + " ack: " + str(ack) + " fin: " + str(fin) + " state: " + str(
        #     self.state) + " close: " + str(close) + " connect: " + str(connect))
        if self.state != self.LISTEN and self.to_addr != to_address:
            return
        if self.state == self.LISTEN:
            if syn:
                self.to_addr = to_address
                self.state = self.SYN_RECV
                syn_ack_packet = packet()
                syn_ack_packet.generate_send_packet(b'', psh=0, syn=1, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.sendto(syn_ack_packet.send_bytes, self.to_addr)
            elif connect:
                self.state = self.SYN_SENT
                syn_packet = packet()
                syn_packet.generate_send_packet(b'', psh=0, syn=1, ack=0, fin=0, seq_num=self.seq_num,
                                                ack_num=self.ack_num, payload_len=0)
                self.sendto(syn_packet.send_bytes, self.to_addr)
            elif close:
                self.state = self.CLOSED
        elif self.state == self.SYN_RECV:
            if ack:
                self.state = self.ESTABLISHED
            if close:
                syn_ack_packet = packet()
                syn_ack_packet.generate_send_packet(b'', psh=0, syn=0, ack=0, fin=1, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.sendto(syn_ack_packet.send_bytes, self.to_addr)
                self.state = self.FIN_WAIT_1
        elif self.state == self.SYN_SENT:
            if close:
                self.state = self.CLOSED
            elif syn and not ack:
                ack_packet = packet()
                ack_packet.generate_send_packet(b'', psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                ack_num=self.ack_num,
                                                payload_len=0)
                self.sendto(ack_packet.send_bytes, self.to_addr)

                self.state = self.SYN_RECV
            elif syn and ack:
                syn_ack_packet = packet()
                syn_ack_packet.generate_send_packet(b'', psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.sendto(syn_ack_packet.send_bytes, self.to_addr)

                self.state = self.ESTABLISHED
        elif self.state == self.ESTABLISHED:
            if close:
                fin_packet = packet()
                fin_packet.generate_send_packet(b'', psh=0, syn=0, ack=0, fin=1, seq_num=self.seq_num,
                                                ack_num=self.ack_num,
                                                payload_len=0)
                self.sendto(fin_packet.send_bytes, self.to_addr)

                self.state = self.FIN_WAIT_1
            elif fin:
                ack_packet = packet()
                ack_packet.generate_send_packet(b'', psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                ack_num=self.ack_num,
                                                payload_len=0)
                self.sendto(ack_packet.send_bytes, self.to_addr)

                self.state = self.CLOSE_WAIT
        elif self.state == self.CLOSE_WAIT:
            if close:
                fin_packet = packet()
                fin_packet.generate_send_packet(b'', psh=0, syn=0, ack=0, fin=1, seq_num=self.seq_num,
                                                ack_num=self.ack_num,
                                                payload_len=0)
                self.sendto(fin_packet.send_bytes, self.to_addr)

                self.state = self.LAST_ACK
        elif self.state == self.LAST_ACK:
            if ack:
                self.state = self.CLOSED
        elif self.state == self.FIN_WAIT_1:
            if fin and not ack:
                syn_ack_packet = packet()
                syn_ack_packet.generate_send_packet(b'', psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.sendto(syn_ack_packet.send_bytes, self.to_addr)
                self.state = self.CLOSING
            elif fin and ack:
                self.state = self.FIN_WAIT_2

        elif self.state == self.FIN_WAIT_2:
            if fin:
                syn_ack_packet = packet()
                syn_ack_packet.generate_send_packet(b'', psh=0, syn=0, ack=1, fin=0, seq_num=self.seq_num,
                                                    ack_num=self.ack_num,
                                                    payload_len=0)
                self.sendto(syn_ack_packet.send_bytes, self.to_addr)
                self.state = self.TIME_WAIT
        elif self.state == self.CLOSING:
            if ack:
                self.state = self.TIME_WAIT
        elif self.state == self.TIME_WAIT:
            sleep(0.002)
            self.state = self.CLOSED
