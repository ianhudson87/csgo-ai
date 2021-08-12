import pyopencl as cl

platforms = cl.get_platforms() # a platform corresponds to a driver (e.g. AMD)
platform = platforms[0] # take first platform
devices = platform.get_devices(cl.device_type.GPU) # get GPU devices of selected platform
device = devices[0] # take first GPU