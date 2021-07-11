import glob
from PIL import Image
import os
import re
import numpy as np
import cv2

class AmmoManager:

    def __init__(self):
        self.current_ammo_amt = None # int of the current ammo amount
        self.previous_ammo_amt = None
        self.ammo_img_ref = {}
        self.default_ammo_amount = 30

        ammo_img_ref_path = "./ammo_images_hud_scaling_0_5"
        img_glob = glob.glob(os.path.join(ammo_img_ref_path, "*.png"))
        for img_path in img_glob:
            ammo_value = int(re.search(r'\d+', os.path.split(img_path)[-1]).group())
            # print(ammo_value)
            img = np.array(Image.open(img_path))
            self.ammo_img_ref[ammo_value] = img
        # print(self.ammo_img_ref)

    def set_current_ammo(self, ammo_img):
        self.previous_ammo_amt = self.current_ammo_amt
        self.current_ammo_amt = self.get_ammo_value(ammo_img)

        # print("prev", self.previous_ammo_amt)
        # print("current", self.current_ammo_amt)

    def get_ammo_value(self, ammo_img):
        ammo_img = np.where(ammo_img == 255, np.uint8(255), np.uint8(0)) # apply threshold filter to image
        for i in range(30,-1,-1):
            if np.array_equal(self.ammo_img_ref[i], ammo_img):
                return i
        else:
            return self.default_ammo_amount

    def isShooting(self):
        if self.current_ammo_amt < self.previous_ammo_amt:
            return True
        return False
        

# a = AmmoManager()
# print(a.ammo_img_ref[12].dtype)
# cv2.imshow("test", a.ammo_img_ref[30])
# cv2.waitKey(0)