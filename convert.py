from PIL import Image
import glob
import cv2
import numpy as np
import os

path = "./logs/good4/images/*.jpeg"
path_new = "./logs/good4/images_new"

glob = glob.glob(path)

for file in glob:
    im = Image.open(file)
    # im = im.convert('RGB') # remove alpha channel
    # b, g, r = im.split() # flip red and blue
    # im = Image.merge("RGB", (r, g, b))
    im = im.resize((180, 80), Image.ANTIALIAS)
    im.save(os.path.join(path_new, os.path.split(file)[-1]))