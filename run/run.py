import time
from mss import mss
import numpy as np
from PIL import Image
from model.SomethingModel import SomethingModel
import cv2
import torch
import sys
sys.path.append("../")
from mouse_input import move_mouse

game_frame_x = 448
game_frame_y = 167
# meta_frame = {'left': game_frame_x+17, 'top': game_frame_y+58, 'width': 500, 'height': 15}
ammo_frame = {'left': game_frame_x+945, 'top': game_frame_y+746, 'width': 20, 'height': 17} # make sure this matches with ammo_img_generator
center_frame = {'left': game_frame_x+220, 'top': game_frame_y+140, 'width': 584, 'height': 488}

framerate = 16
sec_per_frame = 1./framerate
last_frame = time.time()
next_frame = last_frame + sec_per_frame

model_path = "./checkpoints/net20.pth"

model = SomethingModel(hidden_layer_size=256)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-8)
checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
print("here"*100)
model.load_state_dict(checkpoint['model'])
optimizer.load_state_dict(checkpoint['optimizer'])
# model.eval()

print("here"*100)

hidden = None

mouse_table = {
    0: -300,
    1: -200,
    2: -100,
    3: -60,
    4: -30,
    5: -20,
    6: -10,
    7: -5,
    8: -3,
    9: -1,
    10: 0,
    11: 1,
    12: 3,
    13: 5,
    14: 10,
    15: 20,
    16: 30,
    17: 60,
    18: 100,
    19: 200,
    20: 300,
}

while True:
    if time.time() >= next_frame:
        with mss() as sct:
            lag = time.time()-next_frame
            print("lag", lag, sep=":")
            last_frame = next_frame
            next_frame += sec_per_frame

            # screenshot center of screen
            # center_img = np.array(sct.grab(center_frame)) ############## do i need this
            center_img = sct.grab(center_frame)
            im = Image.frombytes("RGB", center_img.size, center_img.bgra, "raw", "BGRX")
            # center_img = center_img[:, :, 0:3]
            # print(np.shape(center_img[:, :, 0:3]))
            # cv2.imshow("test", center_img)
            # im = Image.fromarray(center_img) ##################### this ????????
            # print(total_saved_frames, len(images_cache), sep="a")
            # im = im.convert('RGB') # remove alpha channel
            # b, g, r = im.split() # flip red and blue
            # im = Image.merge("RGB", (r, g, b))
            input = np.array(im.resize((180, 80), Image.ANTIALIAS))
            input = np.expand_dims(input, axis=0)
            input = np.swapaxes(input, 1, 3) / 256
            input = torch.tensor(input).type(torch.float32)

            # print("SHAPE", input.shape)
            # print("here", center_img)

            # cv2.imshow("test", input)

            hidden, y_pred = model((input, hidden)) # state used for LSTM hidden state
            # hidden[0].detach_()
            # hidden[1].detach_()

            # print(y_pred.shape)

            pred = {
                "inputs": torch.argmax(y_pred[:, 0:6]).item(),
                "mouse_x": torch.argmax(y_pred[:, 6:27]).item(),
                "mouse_y": torch.argmax(y_pred[:, 27:48]).item(),
            }

            print(pred['mouse_x'])
            print(pred['mouse_y'])
            move_mouse(mouse_table[pred["mouse_x"]], mouse_table[pred["mouse_y"]])

        
        if cv2.waitKey(33) & 0xFF in (
            ord('q'), 
            27, 
        ):
            break