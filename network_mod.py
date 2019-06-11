# network module for rover
import socket as s
"""
1) create sockets

2) provide send/recieve to rover software

3) manage dropped connections

4) non-blocking

"""


def make_stream_socket():
    return s.socket(s.AF_INET, s.SOCK_STREAM)


class client_socket:
    def __init__(self):
        self.sock = make_stream_socket()


class server_socket:
    def __init__(self, u_ip, u_port):
        self.sock = make_stream_socket()
