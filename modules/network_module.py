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


def make_stream_socket(reuse_addr=True):
    sock = s.socket(s.AF_INET, s.SOCK_STREAM)
    if reuse_addr:
        sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    # sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEPORT, 1)
    return sock


def debug_print(string, print_kwargs={}):
    print(time.strftime("%H:%M:%S: ") + string, **print_kwargs)


def network_msg_print(*args):
    if print_network_msg:
        debug_print(*args)


class client_socket:
    def __init__(self, timeout=5):
        self.sock = make_stream_socket(False)
        self.conn_stat = False
        self.timeout = timeout

    def connect_to(self, port, addr=s.gethostname()):
        self.sock.setblocking(1)
        self.target = (addr, port)
        network_msg_print("attempting to connect to {}".format(self.target))
        while self.conn_stat is False:
            try:
                self.sock.connect(self.target)
                self.conn_stat = True
            except (ConnectionRefusedError):
                time.sleep(3)
                network_msg_print("could not connect to {} (refused), trying again...".format(self.target))
            except (OSError):
                time.sleep(3)
                self.sock.close()
                self.sock = make_stream_socket()
                network_msg_print("could not connect to {} (dead socket), cleaning up...".format(self.target))
        network_msg_print("done")
        self.sock.setblocking(0)
        self.conn_stat = True

    def send_message(self, msg):
        if self.conn_stat:
            _, writeable, errors = select.select([], [self.sock],
                                                 [self.sock], self.timeout)
            if len(writeable) > 0:
                try:
                    writeable[0].send(msg.encode())
                except (ConnectionResetError, ConnectionAbortedError):
                    self.conn_stat = False
                    self.connect_to(self.target[1], self.target[0])
                    self.send_message(msg)
            elif len(errors) > 0:
                network_msg_print("Socket error, attempting to reconnect")
                self.conn_stat = False
                self.connect_to(self.target[1], self.target[0])
                self.send_message(msg)


class server_socket:
    """
    timeout response:
    0: listen again
    1: listen again until max timeout, then dump connection & wait.
    2: listen again until max timeout, then return None
    3: dump connection on first timeout
    4: return None on first timeout

    Future versions:
    -socket just remembers the state it's in, returns after every attempt.
    -successive "read" calls have different effects (timeout response)
    -allow module user to make decisions based on socket/connection state
    """

    def __init__(self, u_port, u_ip=s.gethostname(),
                 timeout=5, max_timeout=60, timeout_response=0):
        self.timeout = timeout
        self.max_timeout = max_timeout
        self.sock = make_stream_socket()
        self.sock.bind((u_ip, u_port))
        self.sock.listen(5)
        self.total_timeout_time = 0

    def get_connection(self):
        self.sock.setblocking(1)
        self.sock.listen(1)
        network_msg_print("waiting for connection... ")
        self.connection, addr = self.sock.accept()
        network_msg_print("got connection from: {}".format(addr))
        self.sock.listen(0)
        self.sock.setblocking(0)

    def get_messages(self):
        msg = None
        try:
            readable, _, errors = select.select([self.connection], [],
                                                [self.connection],
                                                self.timeout)
            if len(errors) > 0:
                # socket in error
                self.connection = False
                raise ConnectionResetError("socket in error")
            elif len(readable) == 0:
                # socket alive, but not readable: timeout
                self.total_timeout_time += self.timeout
                if self.total_timeout_time > self.max_timeout:
                    self.total_timeout_time = 0
                    self.connection = False
                    raise ConnectionResetError("too long since last message")
            elif len(readable) > 0:
                # socket readable
                self.total_timeout_time = 0
                msg = readable[0].recv(2048).decode()
        except ConnectionResetError as e:
            network_msg_print("connection failed: {}\nreaquiring".format(e))
            self.get_connection()
            msg = self.get_messages()
        return msg

    def _handle_timeout(self):
        pass

    def _report_timeout(self):
        pass

    def _handle_dead_connection(self):
        pass


def make_server(u_port, u_ip=s.gethostname(), timeout=5):
    return server_socket(u_port, u_ip, timeout)


def make_client():
    return client_socket()
