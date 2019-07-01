# camera streamer
import modules.network_module as network_module
import time
MODE = {'IP': 'localhost'}
print("=== PiCamera streamer start ===")


def debug_null(*args):
    pass


def get_image_bytes():
    # make the picture
    MODE['cam_fun']()
    # get read bytes from image
    file = open(MODE['filepath'], 'rb')
    img_bytes_str = file.read().decode()
    file.close()
    return img_bytes_str


try:
    from picamera import PiCamera
    camera = PiCamera()
    # adjust light levels requires 2 seconds appaz
    time.sleep(2)
    MODE['filepath'] = ' /home/pi/Desktop/capture.png'
    MODE['cam_fun'] = camera.capture
except Exception as e:
    print(e, "while trying Picamera")
    MODE['filepath'] = '"Test Files"/test.png'
    MODE['cam_fun'] = debug_null


client = network_module.make_client()
client.connect_to(5002, MODE['IP'])
while 1:
    img_bytes_str = get_image_bytes()
    client.send(img_bytes_str)
    # 24 fps hack
    time.sleep(1/24)
