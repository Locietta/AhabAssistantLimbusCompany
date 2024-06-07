# 获取整个显示器的大小
from ctypes import windll
from threading import Lock
import cv2
import numpy as np
import pyautogui

from my_log.my_log import my_log

pyautogui.FAILSAFE = False
lock = Lock()


def win_cap():
    global lock
    with lock:
        try:
            pyautogui.moveTo(1, 1)
        except:
            my_log("error", "鼠标被占用")
        windll.user32.SetProcessDPIAware()
        # 进行全屏截图
        screenshot = pyautogui.screenshot()
        # 将截图转换为OpenCV图像格式
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # 调整截图的大小为1920*1080
        screenshot = screenshot[:1080, :1920]
        # 保存原始截图
        cv2.imwrite("./screenshot.png", screenshot)
        del screenshot