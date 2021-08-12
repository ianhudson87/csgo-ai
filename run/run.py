import time
from mss import mss
import numpy as np
from PIL import Image
from model.SomethingModel import SomethingModel
import cv2
import torch
import sys
sys.path.append("./")
sys.path.append("../")
from mouse_input import move_mouse

# USAGE: python run.py [model_name]

game_frame_x = 448
game_frame_y = 167
# meta_frame = {'left': game_frame_x+17, 'top': game_frame_y+58, 'width': 500, 'height': 15}
ammo_frame = {'left': game_frame_x+945, 'top': game_frame_y+746, 'width': 20, 'height': 17} # make sure this matches with ammo_img_generator
center_frame = {'left': game_frame_x+220, 'top': game_frame_y+140, 'width': 584, 'height': 488}

framerate = 16
sec_per_frame = 1./framerate
last_frame = time.time()
next_frame = last_frame + sec_per_frame
batch_size = 32
images_cache = torch.zeros((batch_size, 3, 180, 80))

model_path = "./checkpoints/" + sys.argv[1]

model = SomethingModel(hidden_layer_size=256)
checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
print("here"*100)
model.load_state_dict(checkpoint['model'])
model.eval()

if torch.cuda.is_available():
    model = model.cuda()

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

cached_image_index = 0

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
            im = Image.frombytes("RGB", center_img.size, center_img.bgra, "raw", "RGBX")
            # center_img = center_img[:, :, 0:3]
            # print(np.shape(center_img[:, :, 0:3]))
            # cv2.imshow("test", center_img)
            # im = Image.fromarray(center_img) ##################### this ????????
            # print(total_saved_frames, len(images_cache), sep="a")
            # im = im.convert('RGB') # remove alpha channel
            # b, g, r = im.split() # flip red and blue
            # im = Image.merge("RGB", (r, g, b))
            im = np.array(im.resize((180, 80), Image.ANTIALIAS))
            print(np.shape(im))
            # cv2.imshow("test", input)
            # im = np.expand_dims(input, axis=0)
            im = np.swapaxes(im, 0, 2) / 256
            im = torch.tensor(im).type(torch.float32)

            # print("SHAPE", input.shape)
            # print("here", center_img)

            print(np.shape(images_cache))
            if cached_image_index < batch_size - 1:
                # cache is not full, fill'r up
                images_cache[cached_image_index] = im
                cached_image_index += 1
                continue
            elif cached_image_index == batch_size - 1:
                images_cache[cached_image_index] = im
                # cache just filled up
                cached_image_index += 1
            else:
                # cache is already full
                print("hi")
                # images_cache[0:batch_size-1] = images_cache[1:batch_size].clone() # shift everything over
                # images_cache[batch_size-1] = im

            # cv2.imshow("test", input)


            input = images_cache.clone()

            if torch.cuda.is_available():
                input = input.cuda()

            hidden, y_pred = model((input, hidden)) # state used for LSTM hidden state
            # hidden[0].detach_()
            # hidden[1].detach_()

            print(y_pred.shape)

            pred = {
                "inputs": torch.argmax(y_pred[0, 0:6]).item(),
                "mouse_x": torch.argmax(y_pred[0, 6:27]).item(),
                "mouse_y": torch.argmax(y_pred[0, 27:48]).item(),
            }

            print(pred['mouse_x'])
            print(pred['mouse_y'])
            # move_mouse(mouse_table[pred["mouse_x"]], mouse_table[pred["mouse_y"]])
            move_mouse(mouse_table[pred["mouse_x"]], 0)

        
        if cv2.waitKey(33) & 0xFF in (
            ord('q'), 
            27, 
        ):
            break