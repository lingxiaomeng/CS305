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
        self.A_name = a_name
        self.A_type = a_type
        self.A_class_name = a_class
        self.A_ttl = a_ttl
        self.A_data_length = a_data_length
        self.A_data = a_data

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class RR:
    def __init__(self, name, type, a_class, data=0, due_date=0):
        self.due_date = due_date
        self.name = name
        self.type = type
        self.a_class = a_class
        self.data = data

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.name == other.name) and (self.type == other.type) and (self.a_class == other.a_class)
