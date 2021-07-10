import pyautogui
import time

def move_mouse(dx, dy):
    pyautogui.moveRel(dx, dy)
    
def click_mouse():
    pyautogui.click()
# pyautogui.click(100, 100)
# pyautogui.moveTo(100, 150)
# start = time.time()
# while time.time() < start + 5:
    # pyautogui.moveRel(1, 0)  # move mouse 10 pixels down
# pyautogui.dragTo(100, 150)
# pyautogui.dragRel(0, 10)  # drag mouse 10 pixels down

