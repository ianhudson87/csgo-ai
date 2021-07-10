import re
import math

class PositionManager:
    
    def __init__(self):
        self.current_position = None # dictionary of position values
        self.previous_position = None
        self.pixels_per_degree = 18.5 # mouse movement pixels needed to change view angle by one degree. (sensitiviy 2.5, raw_input 0, windows 6/11)`
        self.jump_acceleration_threshold = 11 # difference in z position to trigger jump
    
    def set_current_position(self, position_string):
        # input what the getpos command ouputs in csgo as string
        self.previous_position = self.current_position
        self.current_position = self.parse_pos(position_string)

    def parse_pos(self, pos_string):
        # input the what the getpos command ouputs in csgo as string
        # return keystrokes and mouse movement based on change in position
        
        # parse string for position and angle values
        pos_array = re.split(' |;', pos_string)
        
        try:
            pos_dict = {
                "xpos" : float(pos_array[1]),
                "ypos" : float(pos_array[2]),
                "zpos" : float(pos_array[3]),
                "pitch" : float(pos_array[5]),
                "yaw" : float(pos_array[6])
            }
        except:
            pos_dict = self.current_position # occasionally csgo can't write to log file fast enough
        
        return pos_dict
    
    def get_mouse_input(self):
        # using previous position and current position, determine what user mouse input was
        
        delta_yaw = self.current_position["yaw"] - self.previous_position["yaw"]
        
        # handle crossing discontinuity
        if delta_yaw > 180:
            delta_yaw -= 360
        if delta_yaw < -180:
            delta_yaw += 360
        
        delta_pitch = self.current_position["pitch"] - self.previous_position["pitch"]
        
        mouse_input = {
            "mouse_x": delta_yaw * self.pixels_per_degree,
            "mouse_y": delta_pitch * self.pixels_per_degree
        }
        
        return mouse_input
        
    def get_keyboard_input(self):
        # determine wasd and jump
        forward = left = backward = right = jump = False
        
        # find movement angle relative to aim to find wasd
        movement_angle = self.calculate_movement_angle()
        if movement_angle is not None:
            # some movement was made
            yaw_angle = self.current_position["yaw"]
            if yaw_angle < 0: yaw_angle += 360 # map values from [-180, 180) to [0, 360) to be consistent with calculated movement angle
            
            true_movement_angle = (movement_angle - yaw_angle) % 360 # movement angle relative to aim angle
            
            forward = left = backward = right = False
            if true_movement_angle < 22.5:
                forward = True
            elif true_movement_angle < 67.5:
                forward = left = True
            elif true_movement_angle < 112.5:
                left = True
            elif true_movement_angle < 157.5:
                left = backward = True
            elif true_movement_angle < 202.5:
                backward = True
            elif true_movement_angle < 247.5:
                backward = right = True
            elif true_movement_angle < 292.5:
                right = True
            elif true_movement_angle < 337.5:
                right = forward = True
            else:
                forward = True
        
        # determine if jumped
        delta_z = self.current_position["zpos"] - self.previous_position["zpos"]
        if delta_z > self.jump_acceleration_threshold:
            jump = True
        
        # compile info
        keyboard_input = {
            "forward": forward,
            "left": left,
            "backward": backward,
            "right": right,
            "jump": jump
        }
        
        return keyboard_input
        
    def calculate_movement_angle(self):
        delta_x = self.current_position["xpos"] - self.previous_position["xpos"]
        delta_y = self.current_position["ypos"] - self.previous_position["ypos"]
        
        # if delta_x == 0:
            # if delta_y == 0:
                # # did not move
                # return None
            # elif delta_y > 0:
                # # only moved in +y direction
                # return 90
            # else:
                # # only moved in -y direction
                # return 270
        
        if delta_x == 0 and delta_y == 0:
            # did not move
            return None
        
        if delta_x == 0:
            delta_x = 1e-8 # avoid division by 0
            
        angle = math.atan(delta_y / delta_x)
        
        if delta_y >= 0 and delta_x < 0:
            angle += math.pi
            
        if delta_y < 0 and delta_x < 0:
            angle -= math.pi
            
        angle = math.degrees(angle)
        
        if angle < 0: angle += 360
        
        return angle
        
    def get_input(self):
        mouse_input = self.get_mouse_input()
        keyboard_input = self.get_keyboard_input()
        
        return mouse_input | keyboard_input
    
# Pos = PositionManager()
# Pos.set_current_position('setpos 167.048691 11.843389 64.093811;setang 16.885281 63.792023 0.000000')
# Pos.set_current_position('setpos 167.048691 11.843389 64.093811;setang 16.885281 63.792023 0.000000')
# print(Pos.current_position)
# print(Pos.previous_position)
# print(Pos.calculate_movement_angle())