# ================================================== #
# Importation of Default Module
# ================================================== #
import time
import subprocess
from typing import List

# ================================================== #
# Importation of 3rd Party Module
# ================================================== #
from pytictoc import TicToc
import numpy as np
import cv2
import pyautogui as gui

# ================================================== #
# Importation Of Self Development Module
# ================================================== #

# ================================================== #
# Declaration AND Definition Of This Module Variable
# ================================================== #
clock = TicToc()

# Sourcing Of Measurement Table Of GTG RT
pairs = []
tmp = []
for GL1 in np.append(np.arange(0, 255, 48), 255):
    for GL2 in np.append(np.arange(GL1, 255, 48), 255):
        tmp = []
        if (GL2 == GL1):
            continue
        
        tmp.append(GL1)
        tmp.append(GL2)
        pairs.append(tmp)

imgtest = np.zeros((2436, 752, 3), dtype=np.uint8)

# ================================================== #
# Declaration ANd Definition Of This Module Function
# ================================================== #
def VideoOD (fdir: str="", fname: str="",
             RES_V: int=None, RES_H: int=None, RES_C: int=None,
             FPS: int=60, Duration: int=3,
             Conditions: List[List[np.uint8]]=[]):
    width = RES_H 
    hieght = RES_V
    channel = RES_C

    fps = FPS
    sec = Duration
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    video = cv2.VideoWriter(fdir + "\\" + fname, fourcc, float(fps), (width, hieght))

    img = np.zeros((RES_V, RES_H, RES_C), dtype=np.uint8)

    Period = Conditions[-1][0]

    for frame_count in range(fps * sec):
        remainder = frame_count % Period
        for Condition in Conditions:
            if (remainder < Condition[0]):
                img[:] = Condition[1]
                video.write(img.copy())
                break

    video.release()

def MinimizeTargetWindow (wins, targetTitle, wait=1):
    for win in wins:
        if (win.title == targetTitle):
            win.activate()
            time.sleep(wait)
            win.minimize()
            time.sleep(wait)
            return True
    
    return False

def ActivateTargetWindow (wins, targetTitle, wait=1):
    for win in wins:
        if (win.title == targetTitle):
            win.activate()
            time.sleep(wait)
            win.minimize()
            time.sleep(wait)
            win.maximize()
            time.sleep(wait)
            return True
    
    return False

# ================================================== #
# Testing Of This Module
# ================================================== #
if (__name__ == "__main__"):
    # Setting Of Sourcing Of Testing Video
    (RES_V, RES_H, RES_C) = (2436, 752, 3)
    (FPS, Duration) = (60, 10)
    (fdir_video, fname_video) = (r"D:", r"RES_{}_{}_{}_FPS_{}_GL1_{:02}_{:03}_GL2_{:02}_{:03}_GL3_{:02}_{:03}.mp4")
    tEnd_GL1 = 10
    tEnd_GL2 = 11
    tEnd_GL3 = 20
    
    # Setting Of GUI Automation Of CA410
    targetTitle = r"PC Software for Color Analyzer"
    
    fname_MeasurementIdle = r"MeasurementIdle.png"
    fname_MeasurementWorking = r"MeasurementWorking.png"
    fname_FileSavingLevel01 = r"FileSavingLevel01.png"
    fname_FileSavingLevel02 = r"FileSavingLevel02.png"
    fname_FileSavingLevel03 = r"FileSavingLevel03_002.png"
    
    PositionFileSavingLevel = (800, 200)
    PositionFileSavingLevel01 = None
    PositionFileSavingLevel02 = None
    PositionFileSavingLevel03 = None
    tmp = None
    
    origin = gui.position()
    
    clock.tic()
    
    for pair in pairs:
        print(pair)
        
        before = time.time()
        
        # -------------------------------------------------- #
        # Sourcing Tesing Video
        # -------------------------------------------------- #
        if (len(pair) == 2):
            Conditions = [[tEnd_GL1, pair[0]],
                          [tEnd_GL3, pair[1]]]
            
            VideoOD(RES_V=RES_V, RES_H=RES_H, RES_C=RES_C,
                    FPS=FPS, Duration=Duration, Conditions=Conditions,
                    fdir=fdir_video, fname=fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[1][0], Conditions[1][1]))
        elif (len(pair) == 3):
            Conditions = [[tEnd_GL1, pair[0]],
                          [tEnd_GL2, pair[1]],
                          [tEnd_GL3, pair[2]]]
            
            VideoOD(RES_V=RES_V, RES_H=RES_H, RES_C=RES_C,
                    FPS=FPS, Duration=Duration, Conditions=Conditions,
                    fdir=fdir_video, fname=fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1]))
        
        # -------------------------------------------------- #
        # Displaying Testing Video
        # -------------------------------------------------- #
        fpath_video = fdir_video + "\\" + fname_video
        
        SP_PythonVLC = subprocess.Popen(["vlc", "--directx-device={\\.\DISPLAY1}", "--fullscreen", "--play-and-exit",
                                         fpath_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[1][0], Conditions[1][1])])
        
        time.sleep(1)
        
        # -------------------------------------------------- #
        # Checking CA410 Software Before Measurement
        # -------------------------------------------------- #
        wins = gui.getAllWindows()

        if (not ActivateTargetWindow(wins, targetTitle)):
            print("Target Window Not Found Before Measurement")
            exit()
        
        # -------------------------------------------------- #
        #   Triggering Measurement
        # -------------------------------------------------- #
        try:
            gui.click(fname_MeasurementIdle)
            gui.moveTo(origin)
        except:
            print("GUI Component Not Found")
            exit()
        
        # -------------------------------------------------- #
        # Waiting For Ending Of SubProcess
        # -------------------------------------------------- #
        SP_PythonVLC.wait()
        
        # -------------------------------------------------- #
        # Checking CA410 Software After Measurement
        # -------------------------------------------------- #
        wins = gui.getAllWindows()

        if (not ActivateTargetWindow(wins, targetTitle)):
            print("Target Window Not Found After Measurement")
            exit()
        
        # -------------------------------------------------- #
        # Saving Measurement Result
        # -------------------------------------------------- #
        while(not gui.locateOnScreen(fname_MeasurementIdle)):
            pass
        
        gui.rightClick(*PositionFileSavingLevel)
        time.sleep(1)
        
        try:
            counter = 5
            while (counter > 0):
                tmp = gui.locateOnScreen(fname_FileSavingLevel01)
                
                if (tmp != None):
                    break
                else:
                    time.sleep(1)
                    counter = counter - 1
        except:
            print("File Saving Level01 NG")
            exit()
        PositionFileSavingLevel01 = (tmp.left + int(tmp.width/2), tmp.top + int(tmp.height*5/6))
        gui.moveTo(*PositionFileSavingLevel01)
        time.sleep(1)
        
        try:
            tmp = gui.locateOnScreen(fname_FileSavingLevel02)
        except:
            print("File Saving Level02 NG")
            exit()
        PositionFileSavingLevel02 = (tmp.left + int(tmp.width/2), tmp.top + int(tmp.height*1/6))
        gui.click(*PositionFileSavingLevel02)
        time.sleep(1)
        
        try:
            tmp = gui.locateOnScreen(fname_FileSavingLevel03)
        except:
            print("File Saving Level01 NG")
            exit()
        PositionFileSavingLevel03 = (tmp.left + int(tmp.width/2), tmp.top + int(tmp.height*5/6) - 25)
        gui.moveTo(*PositionFileSavingLevel03)
        gui.doubleClick()
        time.sleep(0.5)
        gui.write((fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[1][0], Conditions[1][1])).replace("mp4", "csv"))
        time.sleep(0.5)
        gui.press("enter")
        
        after = time.time()
        
        print(f"Elapsed {after-before}")
    
    MinimizeTargetWindow(wins, targetTitle)
    print("Measurement Done!")
    
    clock.toc()
    