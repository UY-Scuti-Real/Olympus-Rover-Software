import network_module


def decode_message(message):
    if message is not None and len(message) > 0:
        message_array = message.split(',')
        codon_dictionary = {}
        for message in message_array:
            if len(message) > 0 and ":" in message:
                key, value = message.split(":")
                try:
                    codon_dictionary[key] = float(value)
                except Exception:
                    pass
        return codon_dictionary
    else:
        return {}


def print_wave(value):
    n = int(value*10+10)
    print(" "*n, "*")


server_socket = network_module.make_server(5000, 'localhost')
server_socket.get_connection()
while 1:
    message = server_socket.get_messages()
    codon_dictionary = decode_message(message)
    for key, value in codon_dictionary.items():
        print_wave(value)
