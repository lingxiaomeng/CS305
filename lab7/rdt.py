from udp import UDPsocket


class socket(UDPsocket):
    def __init__(self):
        super(socket, self).__init__()
        self.to_addr = None

    def connect(self, address):
        syn_packet = self.generate_packet(b'', 1, 0, 0, 0, 0, 0)
        self.sendto(syn_packet, address)
        data, conn = super().recvfrom(2048)
        self.to_addr = address
        pass

    def accept(self):
        data, addr = super().recvfrom(2048)
        print(data, addr)
        syn_ack_packet = self.generate_packet(b'', 1, 1, 0, 0, 0, 0)
        self.sendto(syn_ack_packet, addr)
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

    def generate_packet(self, payload: bytes, syn, fin, ack, seq: int, seq_ack: int, payload_len):
        head_byte = ((syn << 2) + (fin << 1) + (ack << 0)).to_bytes(2, byteorder='big')
        seq_byte = seq.to_bytes(4, byteorder='big')
        seq_ack_byte = seq_ack.to_bytes(4, byteorder='big')
        payload_len_byte = payload_len.to_bytes(4, byteorder='big')
        to_be_check = head_byte + seq_byte + seq_ack_byte + payload_len_byte + payload
        checksum = self.cal_check_sum(to_be_check)
        send_packet = head_byte + seq_byte + seq_ack_byte + payload_len_byte + checksum.to_bytes(2,
                                                                                                 byteorder='big') + payload
        return send_packet

    def handle_packet(self, recv_packet: bytes):
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
