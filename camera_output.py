# camera output
"""
doing this is going to be interesting. many options. easiest
is a tkinter/pygame front end that just updates the image as it comes.
This is a dangerous approach, though, because tkinter doesn't play
well with cleanup. Pygame, however, deals with it quite well, but requires
setup...
"""
import modules.network_module as network_module
header_bytes = b"\x00\xff\x00\xff"
# server = network_module.make_server(5002, '192.168.1.9')
server = network_module.make_server(5002, "localhost")
server.get_connection()
buffer = b""
while 1:
    bytes_img = server.get_messages(bytes_msg=True)
    if header_bytes in bytes_img:
        print("new frame")
        pre, post = bytes_img.split(header_bytes)
        buffer += pre
        with open("output.png", "wb") as file:
            file.write(buffer)
            file.close()
        buffer = post
    else:
        buffer += bytes_img
