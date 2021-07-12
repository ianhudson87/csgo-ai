import numpy as np
import cv2
from mss import mss
from PIL import Image
import time
# import pytesseract
import os
from keyboard_input import TapKey
from mouse_input import move_mouse
from position_manager import PositionManager
from ammo_manager import AmmoManager
import keyboard
import pandas as pd

# pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe' 
csgo_log_path = 'C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo' # looks for pos_output.log
log_key_hex = 0x42 # DirectInput Key Code for key bind that logs position. Need: bind [key] "con_logfile pos_output.log; getpos; con_logfile ''" in csgo
pos_file = open(os.path.join(csgo_log_path, "pos_output.log"), "r+")
pos_file.truncate(0) # clear contents of file

game_frame_x = 448
game_frame_y = 167
# meta_frame = {'left': game_frame_x+17, 'top': game_frame_y+58, 'width': 500, 'height': 15}
ammo_frame = {'left': game_frame_x+945, 'top': game_frame_y+746, 'width': 20, 'height': 17} # make sure this matches with ammo_img_generator
center_frame = {'left': game_frame_x+220, 'top': game_frame_y+140, 'width': 584, 'height': 488}

framerate = 16
sec_per_frame = 1./framerate
last_frame = time.time()
next_frame = last_frame + sec_per_frame
total_saved_frames = 0
start_time = time.time()

Position = PositionManager()
Ammo = AmmoManager()

images_cache = [] # caching images until save
inputs_cache = [] # caching inputs until save
inputs = pd.DataFrame()

logs_file_path = "./logs/" + str(int(time.time()))
game_image_file_path = os.path.join(logs_file_path, "images")
os.mkdir(logs_file_path)
os.mkdir(game_image_file_path)

start_frame = True

saved = False

def save_data():
    global images_cache
    global inputs_cache
    global inputs
    global start_frame

    start_frame = True # make next frame not calculate input because frames will be discontinuous
    # saving data
    print("saving images and inputs...")
    # saving images
    for i in range(len(images_cache)):
        im = Image.fromarray(images_cache[i])
        # print(total_saved_frames, len(images_cache), sep="a")
        im = im.convert('RGB') # remove alpha channel
        b, g, r = im.split() # flip red and blue
        im = Image.merge("RGB", (r, g, b))
        im = im.resize((180, 80), Image.ANTIALIAS)
        im.save(os.path.join(game_image_file_path, str(total_saved_frames - len(images_cache) + i) + ".jpeg"))

    new_inputs = pd.DataFrame(inputs_cache)
    # print(new_inputs)
    inputs = inputs.append(new_inputs, ignore_index=True)
    inputs.to_csv(os.path.join(logs_file_path, "inputs.csv"))

    # delete cache
    images_cache = []
    inputs_cache = []

    print("done")

while True:
    if total_saved_frames % 1000 == 0 and len(images_cache) != 0:
        save_data()
        next_frame = time.time()
        if time.time()-start_time > 36000:
            break
    if total_saved_frames % 80 == 0 and len(images_cache) != 0:
        TapKey(0x11) # press w key to not get kick by afk
    if keyboard.is_pressed('q'):
        print("q pressed! terminating")
        save_data()
        break
    if time.time() >= next_frame:
        with mss() as sct:
            lag = time.time()-next_frame
            # print("lag", lag, sep=":")
            last_frame = next_frame
            next_frame += sec_per_frame
            
            # POSITIONS STUFF
            TapKey(log_key_hex) # press keybind that logs the position string
            pos_string = pos_file.read()
            if pos_string == "":
                continue # make sure game window is active and logging position
                
            Position.set_current_position(pos_string) # read position and angle from output file
            pos_file.truncate(0) # clear contents of file
            pos_file.seek(0) # return position back to first line

            # AMMO AND SHOOTING STUFF
            # screenshot ammo, save current ammo value
            ammo_img = np.array(sct.grab(ammo_frame))
            Ammo.set_current_ammo(ammo_img)
        
            if start_frame:
                # only one frame, no way to determine mouse and keyboard input, skip screen grab
                start_frame = False
                continue

            total_saved_frames += 1
            # get user inputs by looking at previous and current position and ammo values
            input = Position.get_input() # dictionary
            attacking = Ammo.isShooting() # bool
            input["attacking"] = attacking
            inputs_cache.append(input)

            # screenshot center of screen
            center_img = np.array(sct.grab(center_frame))
            # cv2.imshow("test", center_img)
            images_cache.append(center_img)

        if cv2.waitKey(33) & 0xFF in (
            ord('q'), 
            27, 
        ):
            break