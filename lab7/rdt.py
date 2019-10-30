from udp import UDPsocket


class packet:
    def __init__(self):
        self.syn = None
        self.fin = None
        self.ack = None
        self.seq = None
        self.seq_ack = None
        self.payload_len = None
        self.payload = None
        self.send_bytes = None

    def generate_send_packet(self, payload: bytes, syn, fin, ack, seq: int, seq_ack: int, payload_len):
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.seq = seq
        self.seq_ack = seq_ack
        self.payload_len = payload_len
        self.payload = payload
        head_byte = ((syn << 2) + (fin << 1) + (ack << 0)).to_bytes(2, byteorder='big')
        seq_byte = seq.to_bytes(4, byteorder='big')
        seq_ack_byte = seq_ack.to_bytes(4, byteorder='big')
        payload_len_byte = payload_len.to_bytes(4, byteorder='big')
        to_be_check = head_byte + seq_byte + seq_ack_byte + payload_len_byte + payload
        checksum = self.cal_check_sum(to_be_check)
        self.send_bytes = head_byte + seq_byte + seq_ack_byte + payload_len_byte + checksum.to_bytes(2,
                                                                                                     byteorder='big') + payload

    def handle_recv_packet(self, recv_packet: bytes):
        check = self.cal_check_sum(recv_packet)
        print(check & 0xFFFF)

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
        self.to_addr = None

    def connect(self, address):
        syn_packet = packet()
        syn_packet.generate_send_packet(b'', syn=1, ack=0, seq=0, seq_ack=0, fin=0, payload_len=0)
        self.sendto(syn_packet.send_bytes, address)
        data, conn = super().recvfrom(2048)
        print(data)
        self.to_addr = address
        pass

    def accept(self):
        data, addr = super().recvfrom(2048)
        print(data, addr)
        syn_ack_packet = packet()
        syn_ack_packet.generate_send_packet(b'', 1, 1, 0, 0, 0, 0)
        self.sendto(syn_ack_packet.send_bytes, addr)
        remote_sock = self
        remote_sock.to_addr = addr
        return remote_sock, addr

    def close(self):
        pass

    def recv(self, bufsize):
        data, addr = super().recvfrom(2048)
        print('received: {} {}'.format(data, addr))
        return data

    def send(self, data: bytes, flags: int = ...):
        super().sendto(data, self.to_addr)
        pass
