import network_module

server_sock = network_module.make_server(5001, 'localhost')
client_sock = network_module.make_client()

client_sock.connect_to(5000, 'localhost')
server_sock.get_connection()
while 1:
    message = server_sock.get_messages()
    client_sock.send_message(message)
