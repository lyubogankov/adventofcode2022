# std library
import time
from collections import namedtuple
# third party
import mss
import pyautogui

ScreenshotParams = namedtuple('ScreenshotParams', ['topoffset', 'leftoffset', 'width', 'height', 'monitor', 'savefolder', 'framefolder'])

_screenshotter = mss.mss()  # just make one

def screenshot(screenshotparams, sim_iteration, screenshotter=_screenshotter):
    # with mss.mss() as screenshotter:
    mon_info = screenshotter.monitors[screenshotparams.monitor]
    frame = screenshotter.grab({
        'top'    : mon_info['top']  + screenshotparams.topoffset, 
        'left'   : mon_info['left'] + screenshotparams.leftoffset, 
        'width'  : screenshotparams.width, 
        'height' : screenshotparams.height,
        'mon'    : screenshotparams.monitor
    })
    saveimg = f'/home/lyubo/script/advent_of_code/2022/media/{screenshotparams.savefolder}/{screenshotparams.framefolder}/frame_{sim_iteration:05}.png'
    mss.tools.to_png(frame.rgb, frame.size, output=saveimg)
    time.sleep(0.1)
    # move the mouse to keep the computer from going to sleep
    pyautogui.move(0, -1)
    pyautogui.move(0,  1)