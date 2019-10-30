from udp import UDPsocket


class receiver_FSM:
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
        self.state = self.CLOSED


class packet:
    def __init__(self):
        self.head = None
        self.psh = None
        self.syn = None
        self.fin = None
        self.ack = None
        self.seq = None
        self.seq_ack = None
        self.payload_len = None
        self.payload = None
        self.send_bytes = None
        self.checksum = 0

    def generate_send_packet(self, payload: bytes, psh: int, syn: int, fin: int, ack: int, seq: int, seq_ack: int,
                             payload_len):
        self.psh = psh
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.seq = seq
        self.seq_ack = seq_ack
        self.payload_len = payload_len
        self.payload = payload
        self.head = ((psh << 3) + (syn << 2) + (fin << 1) + (ack << 0))
        head_byte = self.head.to_bytes(2, byteorder='big')
        seq_byte = seq.to_bytes(4, byteorder='big')
        seq_ack_byte = seq_ack.to_bytes(4, byteorder='big')
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
        self.seq = (recv_packet[2] << 24) + (recv_packet[3] << 16) + (recv_packet[4] << 8) + (recv_packet[5] << 0)
        self.seq_ack = (recv_packet[6] << 24) + (recv_packet[7] << 16) + (recv_packet[8] << 8) + (recv_packet[9] << 0)
        self.payload_len = (recv_packet[10] << 24) + (recv_packet[11] << 16) + (recv_packet[12] << 8) + (
                recv_packet[13] << 0)
        self.payload = recv_packet[14:]

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


class socket(UDPsocket):
    def __init__(self):
        super(socket, self).__init__()
        # self.setblocking(False)
        self.to_addr = None
        self.seq_num = 0
        self.ack_num = 0
        self.window_size = 4
        self.max_payload_len = 8

    def connect(self, address):
        syn_packet = packet()
        syn_packet.generate_send_packet(b'', psh=0, syn=1, ack=0, seq=0, seq_ack=0, fin=0, payload_len=0)
        self.sendto(syn_packet.send_bytes, address)
        data, conn = super().recvfrom(2048)
        syn_ack_packet = packet()
        syn_ack_packet.handle_recv_packet(data)
        if syn_ack_packet.checksum == 0:
            if syn_ack_packet.head == 0b0101:
                ack_packet = packet()
                ack_packet.generate_send_packet(b'', psh=0, syn=0, ack=1, seq=1, seq_ack=1, fin=0, payload_len=0)
                self.to_addr = address
                print("connect")
            else:
                print("error")
        else:
            print("Found error in syn_ack_packet")

    def accept(self):
        while True:
            try:
                data, addr = super().recvfrom(2048)
                syn_packet = packet()
                syn_packet.handle_recv_packet(data)
                if syn_packet.checksum == 0:
                    if syn_packet.head == 0b0100:
                        syn_ack_packet = packet()
                        syn_ack_packet.generate_send_packet(b'', psh=0, syn=1, ack=1, seq=0, seq_ack=1, fin=0,
                                                            payload_len=0)
                        self.sendto(syn_ack_packet.send_bytes, addr)
                        remote_sock = self
                        remote_sock.to_addr = addr
                        return remote_sock, addr
                else:
                    print("Found error in syn_packet")
            except BlockingIOError:
                pass

    def close(self):
        pass

    def recv(self, bufsize):
        data, addr = super().recvfrom(2048)
        print('received: {} {}'.format(data, addr))
        return data

    def send(self, data: bytes, flags: int = ...):
        super().sendto(data, self.to_addr)
        pass
