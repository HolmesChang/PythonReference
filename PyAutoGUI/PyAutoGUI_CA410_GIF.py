import time
from pytictoc import TicToc
import numpy as np
import matplotlib.image as img
from imageio import mimsave
import pyautogui as gui

clock = TicToc()

pairs = []
tmp =[]
for GL1 in np.append(np.arange(0, 255, 48), 255):
    for GL2 in np.append(np.arange(GL1, 255, 48), 255):
        tmp = []
        if (GL2 == GL1):
            continue
        
        tmp.append(GL1)
        tmp.append(GL2)
        pairs.append(tmp)

imgtest = np.zeros((2436, 752, 3), dtype=np.uint8)

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
    #   Displaying Pattern01
    # -------------------------------------------------- #
    imgout = []
    for i in np.arange(5):
        imgtest[:] = pair[0]
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgtest[:] = pair[1]
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
        imgout.append(imgtest.copy())
    mimsave("./../PyGLet/TestingPattern.gif", imgout, duration=0.03)
    time.sleep(3)
    gui.click(1800, 200)
    gui.moveTo(origin)

    wins = gui.getAllWindows()

    if (not ActivateTargetWindow(wins, targetTitle)):
        print("Target Window Not Found")
        exit()

    # -------------------------------------------------- #
    #   Creating Pattern02
    # -------------------------------------------------- #
    #imgtest[:, :, :] = pair[1]
    #img.imsave(r"./../PyGLet/TestingPattern.bmp", imgtest)
    #time.sleep(3)

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
    #   Displaying Pattern02
    # -------------------------------------------------- #
    #while(not gui.locateOnScreen(fname_MeasurementWorking)):
    #    pass
    """
    if (pair[1] == 0):
        time.sleep(2.1)
    if (pair[1] == 192):
        time.sleep(2.1)
    else:
        time.sleep(0.8)
    gui.click(1800, 200)
    gui.moveTo(origin)
    """
    
    # -------------------------------------------------- #
    #   Saving Measurement Result
    # -------------------------------------------------- #
    while(not gui.locateOnScreen(fname_MeasurementIdle)):
        pass

    gui.rightClick(*PositionFileSavingLevel)
    time.sleep(0.5)

    try:
        tmp = gui.locateOnScreen(fname_FileSavingLevel01)
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
    #gui.moveRel(200, 0)
    #gui.click()
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
    gui.write("WhiteGL{:03}TogglingGL{:03}_Center.csv".format(pair[0], pair[1]))
    time.sleep(0.5)
    gui.press("enter")

    after = time.time()

    print(f"Elapsed {after-before}")

clock.toc()