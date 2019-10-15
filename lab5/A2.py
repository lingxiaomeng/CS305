from dns.resolver import query
from dns import rdatatype

udp_query = query(qname='www.sina.com.cn', rdtype=rdatatype.A, tcp=False)
tcp_query = query(qname='www.sina.com.cn', rdtype=rdatatype.A, tcp=True)

print(udp_query.response)
print(tcp_query.response)
