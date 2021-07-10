# ammo image generator
from mss import mss
import numpy as np
from PIL import Image
import os
from keyboard_input import PressKey, ReleaseKey
from mouse_input import click_mouse
import time

game_frame_x = 448
game_frame_y = 167
ammo_frame = {'left': game_frame_x+873, 'top': game_frame_y+730, 'width': 38, 'height': 30}

starting_ammo_count = 0

img_save_path = "./ammo_images"

PressKey(0x38)
time.sleep(0.2)
PressKey(0x0F)
time.sleep(0.2)
ReleaseKey(0x0F)
time.sleep(0.2)
ReleaseKey(0x38)

for i in range(starting_ammo_count+1):

    ammo_count = starting_ammo_count - i
    # input("press enter to take image of ammo="+ str(ammo_count))
    with mss() as sct:
        ammo_img = np.array(sct.grab(ammo_frame))
        ammo_img = np.where(ammo_img == 255, np.uint8(255), np.uint8(0))
        im = Image.fromarray(ammo_img)
        im.save(os.path.join(img_save_path, "ammo_"+ str(ammo_count)+ ".png"))
        # im.save(os.path.join(img_save_path, "ammo_", str(ammo_count)), "png")
        # im.save("./ammo_images/test.png")

    click_mouse()

    time.sleep(0.2)