
class Question:
    def __init__(self, qname, qtype, qclass):
        self.QNAME = qname
        self.QTYPE = qtype
        self.QCLASS = qclass

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Answer:
    def __init__(self, a_name, a_type, a_class, a_ttl, a_data_length, a_data):
        self.A_data = a_data
        self.A_name = a_name
        self.A_data_length = a_data_length
        self.A_ttl = a_ttl
        self.A_class_name = a_class
        self.A_type = a_type


    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

