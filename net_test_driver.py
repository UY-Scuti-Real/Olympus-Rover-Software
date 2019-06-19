import network_module
import message_format_module


def print_wave(value):
    n = int(value*10+10)
    print(" "*n, "*")


server_socket = network_module.make_server(5000, 'localhost')
server_socket.get_connection()
while 1:
    message = server_socket.get_messages()
    codon_dictionary = message_format_module.get_valid_cmds(message)
    for key, value in codon_dictionary.items():
        print_wave(value)
