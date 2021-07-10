import numpy as np
import cv2
from mss import mss
from PIL import Image
import time
import pytesseract
import os
from keyboard_input import TapKey
from mouse_input import move_mouse
from position_manager import PositionManager
from ammo_manager import AmmoManager

pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe' 
csgo_log_path = 'C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo' # looks for pos_output.log
log_key_hex = 0x44 # DirectInput Key Code for key bind that logs position. Need: bind [key] "con_logfile pos_output.log; getpos; con_logfile ''" in csgo
pos_file = open(os.path.join(csgo_log_path, "pos_output.log"), "r+")
pos_file.truncate(0) # clear contents of file

game_frame_x = 448
game_frame_y = 167
# meta_frame = {'left': game_frame_x+17, 'top': game_frame_y+58, 'width': 500, 'height': 15}
ammo_frame = {'left': game_frame_x+873, 'top': game_frame_y+730, 'width': 38, 'height': 30}
center_frame = {'left': game_frame_x+220, 'top': game_frame_y+140, 'width': 584, 'height': 488}

framerate = 16
sec_per_frame = 1./framerate
last_frame = time.time()
next_frame = last_frame + sec_per_frame
total_saved_frames = 0

Position = PositionManager()
Ammo = AmmoManager()

images = []

while True:
    if time.time() >= next_frame:
        lag = time.time()-next_frame
        # if lag > 1:
            # print("bad lag")
        # print("Lag: ", lag)
        last_frame = next_frame
        next_frame += sec_per_frame
        
        # POSITIONS STUFF
        TapKey(log_key_hex) # press keybind that logs the position string
        pos_string = pos_file.read()
        if pos_string == "":
            continue # make sure game window is active and logging position
            
        total_saved_frames += 1
        Position.set_current_position(pos_string) # read position and angle from output file
        pos_file.truncate(0) # clear contents of file
        pos_file.seek(0) # return position back to first line

        # AMMO AND SHOOTING STUFF
        with mss() as sct:
            # screenshot ammo, determine if shooting
            ammo_img = np.array(sct.grab(ammo_frame))
            Ammo.set_current_ammo(ammo_img)
            cv2.imshow('test', np.array(ammo_img))
        
        # print(total_saved_frames)
        if total_saved_frames == 1:
            # only one frame, no way to determine mouse and keyboard input, skip screen grab
            continue
        else:
            input = Position.get_input() # dictionary
            attacking = Ammo.isShooting() # bool
            input["attacking"] = attacking
            # print(Position.current_position, Position.previous_position, sep = " ")
            # print(Position.current_position["yaw"], Position.previous_position["yaw"], Position.get_mouse_input(), sep=" ")
            # print(Position.calculate_movement_angle())
            # print(Position.get_mouse_input())
            # print(Position.get_input())
            # Position.get_input() # using previous position and current position, determine what user input
            # parse_pos(current_pos, previous_pos)
            
        
        with mss() as sct:
            ### grab meta data ###
            # meta_grab = sct.grab(meta_frame)
            # meta_img = Image.frombytes(00
                # 'RGB', 
                # (meta_grab.width, meta_grab.height), 
                # meta_grab.rgb, 
            # )
            # cv2.imshow('new', np.array(meta_img))
            # meta_img = np.array(sct.grab(meta_frame))
            # meta_data = pytesseract.image_to_string(meta_img, config="--psm 13")
            # print(meta_data)
            # cv2.imshow("OpenCV/Numpy normal", meta_img)
            
            ### grab center of screen ###
            # center_grab = sct.grab(center_frame)
            # center_img = Image.frombytes(
                # 'RGB', 
                # (center_grab.width, center_grab.height), 
                # center_grab.rgb, 
            # )
            
            # screenshot center of screen
            center_img = np.array(sct.grab(center_frame))
            images.append(center_img)

            # ammo_count = pytesseract.image_to_string(ammo_img, config="--psm 0")
            # print("a", ammo_count, "b")
        
        
        # print(np.shape(img))
        # print("Total frames: ", total_frames)
    if cv2.waitKey(33) & 0xFF in (
        ord('q'), 
        27, 
    ):
        break