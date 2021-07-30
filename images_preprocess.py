# create hdf5 file of all of the images. https://stackoverflow.com/questions/66631284/convert-a-folder-comprising-jpeg-images-to-hdf5
import h5py
import cv2
import os
import glob
import sys
import numpy as np

images_path = "./logs/" + sys.argv[1]
print("applying preprocessing to:", images_path)

# rename images so that it actually goes 1, 2, 3, ... when loading
rename = True
if rename:
  images_glob = glob.glob(images_path+"/images" + "/*.jpeg")
  # print(images_glob)
  i=0
  for image_path in images_glob:
    i+=1
    number_with_ext = os.path.split(image_path)[-1]
    number = os.path.splitext(number_with_ext)[0]
    number = number.zfill(8)
    # print((images_path+"/images/{number}.jpeg").format(number=number))
    os.rename(image_path, (images_path+"/images/{number}.jpeg").format(number=number))
    # if i>1000: break
else:
  print("not renaming files with padded zeros")



# create hdf5
preprocess = True
if preprocess:
  IMG_WIDTH = 180
  IMG_HEIGHT = 80

  h5file = os.path.join(images_path, 'import_images.h5')
  images_glob = glob.glob(images_path+"/images" + "/*.jpeg")
  images_glob.sort()

  nfiles = len(images_glob)
  print(f'count of image files nfiles={nfiles}')

  # resize all images and load into a single dataset
  with h5py.File(h5file,'w') as  h5f:
      img_ds = h5f.create_dataset('images',shape=(nfiles, IMG_HEIGHT, IMG_WIDTH, 3), dtype=np.uint8)
      for cnt, ifile in enumerate(images_glob) :
          if cnt%100 == 99:
              print(cnt)
          img = cv2.imread(ifile, cv2.IMREAD_COLOR)
          # or use cv2.IMREAD_GRAYSCALE, cv2.IMREAD_UNCHANGED
          # img_resize = cv2.resize( img, (IMG_WIDTH, IMG_HEIGHT) )
          img_ds[cnt:cnt+1:,:,:] = img