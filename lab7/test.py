def cal_check_sum(msg: bytes):
    s = 0  # Binary Sum

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        if (i + 1) < len(msg):
            s += (msg[i] << 8) + (msg[i + 1])
        elif (i + 1) == len(msg):
            s += msg[i]
        s = s + (s >> 16)
    s = ~s & 0xFFFF
    return s


def generate_packet(payload: bytes, syn, fin, ack, seq: int, seq_ack: int, payload_len):
    head_byte = ((syn << 2) + (fin << 1) + (ack << 0)).to_bytes(2, byteorder='big')
    seq_byte = seq.to_bytes(4, byteorder='big')
    seq_ack_byte = seq_ack.to_bytes(4, byteorder='big')
    payload_len_byte = payload_len.to_bytes(4, byteorder='big')
    to_be_check = head_byte + seq_byte + seq_ack_byte + payload_len_byte + payload
    checksum = cal_check_sum(to_be_check)
    send_packet = head_byte + seq_byte + seq_ack_byte + payload_len_byte + checksum.to_bytes(2,
                                                                                             byteorder='big') + payload
    return send_packet


def handle_packet(recv_packet: bytes):
    check = cal_check_sum(recv_packet)
    print(check & 0xFFFF)


packet = generate_packet(b'hello', 1, 1, 1, 1, 1, 5)

handle_packet(packet)
