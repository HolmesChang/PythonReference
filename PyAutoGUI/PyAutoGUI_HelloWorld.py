import time
import pyautogui as gui

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
fname_FileSavingLevel01 = r"FileSavingLevel01.png"
fname_FileSavingLevel02 = r"FileSavingLevel02.png"
fname_FileSavingLevel03 = r"FileSavingLevel03_002.png"

PositionFileSavingLevel = (800, 200)
PositionFileSavingLevel01 = None
PositionFileSavingLevel02 = None
PositionFileSavingLevel03 = None
tmp = None

wins = gui.getAllWindows()

if (not ActivateTargetWindow(wins, targetTitle)):
    print("Target Window Not Found")
    exit()

try:
    gui.click(fname_MeasurementIdle)
except:
    print("GUI Component Not Found")
    exit()
time.sleep(3)

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
gui.write("Test.csv")
time.sleep(0.5)
gui.press("enter")