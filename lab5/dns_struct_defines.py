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


class RR:
    def __init__(self, name, name_original, a_type, a_class, data='', due_date=0, data_length=0):
        self.NAME = name
        self.TYPE = a_type
        self.DATA = data
        self.CLASS = a_class
        if data_length == 0:
            self.DATA_LENGTH = int(len(self.DATA) / 2)
        else:
            self.DATA_LENGTH = data_length
        self.DUE_DATE = due_date
        self.NAME_Original = name_original

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other.TYPE == RR_type.CNAME:
            return self.NAME_Original == other.NAME_Original
        else:
            return self.NAME_Original == other.NAME_Original and self.TYPE == other.TYPE


class Question(RR):
    def __init__(self, qname, qtype, qclass, qname_original):
        super().__init__(name=qname, name_original=qname_original, a_type=qtype, a_class=qclass, data='', data_length=0,
                         due_date=0)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Answer(RR):
    def __init__(self, a_name, a_type, a_class, a_ttl, a_data_length, a_data, a_name_original):
        super().__init__(name=a_name, name_original=a_name_original, a_type=a_type, a_class=a_class,
                         data_length=a_data_length, due_date=0, data=a_data)
        self.A_ttl = a_ttl

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()
