# network module for rover
import socket as s
import select
import time
"""
1) create sockets
2) provide send/recieve to rover software
3) manage dropped connections
4) non-blocking
"""
print_network_msg = True


def make_stream_socket():
    sock = s.socket(s.AF_INET, s.SOCK_STREAM)
    sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEPORT, 1)
    return sock


def debug_print(string, print_kwargs={}):
    print(time.strftime("%H:%M:%S: ") + string, **print_kwargs)


def network_msg_print(*args):
    if print_network_msg:
        debug_print(*args)


class client_socket:
    def __init__(self):
        self.sock = make_stream_socket()


class server_socket:
    def __init__(self, u_port, u_ip=s.gethostname(), timeout=0.2):
        self.sock = make_stream_socket()
        self.sock.bind((u_ip, u_port))
        self.timeout = timeout

    def get_connection(self):
        self.sock.listen(1)
        self.sock.setblocking(1)
        network_msg_print("waiting for connection... ")
        connection, addr = self.sock.accept()
        network_msg_print("got connection from: {}".format(addr))
        self.sock.listen(0)
        self.sock.setblocking(0)
        self.connection = connection
        return connection

    def get_messages(self):
        try:
            readable, _, errors = select.select(
                        [self.connection],
                        [],
                        [self.connection],
                        self.timeout)
            if len(errors) > 0:
                self.connection = False
                return False
            elif len(readable) == 0:
                return None
            msg = readable[0].recv(2048)
            return msg.decode()
        except ConnectionResetError:
            network_msg_print("connection failed, reaquiring")
            self.get_connection()
            messages = self.get_messages()
            return messages.decode()


def make_server(u_port, u_ip=s.gethostname()):
    return server_socket(u_port, u_ip)
