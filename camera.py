# camera streamer
import modules.network_module as network_module
import time
# MODE = {'IP': '192.168.1.9'}
MODE = {"IP": "localhost"}
header_bytes = b"\x00\xff\x00\xff"
print("=== PiCamera streamer start ===")


def debug_null(*args):
    pass


def get_image_bytes():
    # make the picture
    MODE['cam_fun'](MODE['filepath'])
    # get read bytes from image
    file = open(MODE['filepath'], 'rb')
    img_bytes_str = file.read()
    file.close()
    return img_bytes_str


try:
    from picamera import PiCamera
    camera = PiCamera()
    # adjust light levels requires 2 seconds appaz
    time.sleep(2)
    camera.start_preview()
    MODE['filepath'] = '/home/pi/Desktop/olympus_rover/capture.png'
    MODE['cam_fun'] = camera.capture
    print("Camera started...")
except Exception as e:
    print(e, "while trying Picamera")
    MODE['filepath'] = 'test_img.png'
    MODE['cam_fun'] = debug_null


client = network_module.make_client()
client.connect_to(5002, MODE['IP'])
try:
    while 1:
        img_bytes_str = header_bytes + get_image_bytes()
        client.send_message(img_bytes_str, bytes_msg=True)
        # 24 fps hack
        # time.sleep(1/24)
        time.sleep(1)
except KeyboardInterrupt:
    camera.stop_preview()
