# camera output
"""
doing this is going to be interesting. many options. easiest
is a tkinter/pygame front end that just updates the image as it comes.
This is a dangerous approach, though, because tkinter doesn't play
well with cleanup. Pygame, however, deals with it quite well, but requires
setup...
"""
import modules.network_module as network_module

server = network_module.make_server(5002, '192.168.1.9')
server.get_connection()
while 1:
    img_str = server.get_messages()
    file = open("output_test.png", "wb")
    file.write(img_str.encode())
    file.close()
