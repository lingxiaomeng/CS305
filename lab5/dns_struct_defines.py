class RR_type:
    NONE = 0
    A = 1
    NS = 2
    MD = 3
    MF = 4
    CNAME = 5
    SOA = 6
    MB = 7
    MG = 8
    MR = 9
    NULL = 10
    WKS = 11
    PTR = 12
    HINFO = 13
    MINFO = 14
    MX = 15
    TXT = 16
    RP = 17
    AFSDB = 18
    X25 = 19
    ISDN = 20
    RT = 21
    NSAP = 22
    NSAP_PTR = 23
    SIG = 24
    KEY = 25
    PX = 26
    GPOS = 27
    AAAA = 28
    LOC = 29
    NXT = 30
    SRV = 33
    NAPTR = 35
    KX = 36
    CERT = 37
    A6 = 38
    DNAME = 39
    OPT = 41
    APL = 42
    DS = 43
    SSHFP = 44
    IPSECKEY = 45
    RRSIG = 46
    NSEC = 47
    DNSKEY = 48
    DHCID = 49
    NSEC3 = 50
    NSEC3PARAM = 51
    TLSA = 52
    HIP = 55
    CDS = 59
    CDNSKEY = 60
    OPENPGPKEY = 61
    CSYNC = 62
    SPF = 99
    UNSPEC = 103
    EUI48 = 108
    EUI64 = 109
    TKEY = 249
    TSIG = 250
    IXFR = 251
    AXFR = 252
    MAILB = 253
    MAILA = 254
    ANY = 255
    URI = 256
    CAA = 257
    AVC = 258
    TA = 32768
    DLV = 32769


class Question:
    def __init__(self, qname, qtype, qclass, qname_original):
        self.QNAME = qname
        self.QTYPE = qtype
        self.QCLASS = qclass
        self.QNAME_original = qname_original

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Answer:
    def __init__(self, a_name, a_type, a_class, a_ttl, a_data_length, a_data, a_name_original):
        self.A_name = a_name
        self.A_type = a_type
        self.A_class = a_class
        self.A_ttl = a_ttl
        self.A_data_length = a_data_length
        self.A_data = a_data
        self.A_name_original = a_name_original

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class RR:
    def __init__(self, name, a_type, a_class, data='', due_date=0, data_length=0):
        self.name = name
        self.a_type = a_type
        self.data = data
        self.a_class = a_class
        self.data_length = int(len(self.data) / 2)
        self.due_date = due_date

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name
