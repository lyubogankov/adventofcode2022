# std library
import time
from collections import namedtuple
# third party
import mss
import pyautogui

ScreenshotParams = namedtuple('ScreenshotParams', ['topoffset', 'leftoffset', 'width', 'height', 'monitor', 'framefolder'])

def screenshot(screenshotter, screenshotparams, sim_iteration, savefolder=''):
    # with mss.mss() as screenshotter:
    mon_info = screenshotter.monitors[screenshotparams.monitor]  # my second monitor
    frame = screenshotter.grab({
        'top'    : mon_info['top']  + screenshotparams.topoffset, 
        'left'   : mon_info['left'] + screenshotparams.leftoffset, 
        'width'  : screenshotparams.width, 
        'height' : screenshotparams.height,
        'mon'    : screenshotparams.monitor
    })
    mss.tools.to_png(frame.rgb, frame.size, output=f'/home/lyubo/script/advent_of_code/2022/media/{savefolder}/{screenshotparams.framefolder}/frame_{sim_iteration}.png')
    time.sleep(0.1)
    # move the mouse to keep the computer from going to sleep
    pyautogui.move(0, -1)
    pyautogui.move(0,  1)