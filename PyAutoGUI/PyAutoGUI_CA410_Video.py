# ================================================== #
# Importation of Default Module
# ================================================== #
import os
import time
import subprocess
from typing import List

# ================================================== #
# Importation of 3rd Party Module
# ================================================== #
from pytictoc import TicToc
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as IUS
from PyAstronomy import pyaC
import cv2
import skvideo.io
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
#pairs = [[0, 192]]

EnOD = True
EnODAutoOptimize = True
IsODDone = False
ODStart = -8
ODStep = 2
ODEnd = 64
TmpOD = {}
TmpOD["From"] = 0
TmpOD["To"] = 0
TmpOD["OD"] = 0
ODTable = []

imgtest = np.zeros((2436, 752, 3), dtype=np.uint8)

# ================================================== #
# Declaration ANd Definition Of This Module Function
# ================================================== #
def VideoOD (fdir: str="", fname: str="",
             RES_V: int=None, RES_H: int=None, RES_C: int=None,
             FPS: int=60, Duration: int=3,
             Conditions: List[List[np.uint8]]=[], lib: str="OpenCV"):
    width = RES_H 
    height = RES_V
    channel = RES_C

    fps = FPS
    sec = Duration
    
    if (lib == "OpenCV"):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        video = cv2.VideoWriter(fdir + "\\" + fname, fourcc, float(fps), (width, height))

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
    
    if (lib == "FFMPEG"):
        writer = skvideo.io.FFmpegWriter(fdir + "\\" + fname,
                                         inputdict={'-r': str(fps), '-s':'{}x{}'.format(width, height)},
                                         outputdict={
                                            '-r': str(fps),
                                            '-vcodec': 'libx264',  #use the h.264 codec
                                            '-crf': '0',           #set the constant rate factor to 0, which is lossless
                                            '-preset':'ultrafast'   #the slower the better compression, in princple, try #veryslow #fast
                                                                #other options see https://trac.ffmpeg.org/wiki/Encode/H.264
                                         }
        )
        
        img = np.zeros((RES_V, RES_H, RES_C), dtype=np.uint8)

        Period = Conditions[-1][0]
        
        for frame_count in range(fps * sec):
            remainder = frame_count % Period
            for Condition in Conditions:
                if (remainder < Condition[0]):
                    img[:] = Condition[1]
                    writer.writeFrame(img.copy())  #write the frame as RGB not BGR
                    break

        writer.close() #close the writer

def MinimizeTargetWindow (wins, targetTitle, wait=0.5):
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

def CalcMPRT (fdir: str=r"C:\Users\HolmesChang\Desktop", fname: str="", RES_Time: np.float64=0.00001, tFrame: np.float64=0.016667, UnitRT: np.float64=0.001, Thres: np.float64=0.0025):
    if (fname == ""):
        print("Please Input Correct File Name")
        return None
    
    data_raw = np.loadtxt(fname=(fdir+ "\\" + fname), delimiter=",", skiprows=9, usecols=(0, 1))
    
    X_New = np.arange(0, data_raw[-1, 0]+RES_Time, RES_Time)
    S = IUS(data_raw[:, 0], data_raw[:, 1], k=1)
    Y_New = S(X_New)
    
    Kernel = np.ones(int(np.ceil(tFrame/RES_Time))) / np.ceil(tFrame/RES_Time)
    Y_New_LPF_60Hz = np.convolve(Y_New, Kernel, "valid")
    
    # Data Plateau
    Y_New_Diff = np.abs(Y_New_LPF_60Hz[1::] - Y_New_LPF_60Hz[0:-1])
    
    Y_New_Diff[Y_New_Diff < Thres] = 0
    
    TmpIndex = 0
    TmpWidth = 0
    TmpPlateau = []
    ListPlateau = []
    IsZeroStart = False
    for (Index, Element) in enumerate(Y_New_Diff):
        if (Element == 0):
            if (not IsZeroStart):
                TmpIndex = Index
                TmpWidth += 1
                IsZeroStart = True
            else:
                TmpWidth += 1
        else:
            if (IsZeroStart):
                TmpPlateau = [TmpIndex, TmpWidth]
                ListPlateau.append(TmpPlateau)
                TmpIndex = 0
                TmpWidth = 0
                IsZeroStart = False
    
    for Plateau in ListPlateau:
        if (Plateau[1] < tFrame):
            Y_New_Diff[Plateau[0]:np.sum(Plateau)] = Thres
    
    Min_Plateau = np.min((Y_New_LPF_60Hz[1::])[Y_New_Diff == 0])
    Max_Plateau = np.max((Y_New_LPF_60Hz[1::])[Y_New_Diff == 0])
    # Data Plateau/
    
    Min = np.min(Y_New_LPF_60Hz)
    Max = np.max(Y_New_LPF_60Hz)
    (Xc_10, Xi_10) = pyaC.zerocross1d(X_New[(len(Kernel)-1)::], Y_New_LPF_60Hz-(Min+0.1*(Max-Min)), getIndices=True)
    (Xc_90, Xi_90) = pyaC.zerocross1d(X_New[(len(Kernel)-1)::], Y_New_LPF_60Hz-(Min+0.9*(Max-Min)), getIndices=True)
    
    # OverShooting Detection
    IsDataOS = False
    if (Max > Max_Plateau):
        IsDataOS = True
    # OverShooting Detection/
    
    PointTransition = []
    for x in Xi_10:
        PointTransition.append(("10", x+1))
    for x in Xi_90:
        PointTransition.append(("90", x+1))
    PointTransition.sort(key=lambda x: x[1])
    
    RisingTime = 0
    CntRisingEdge = 0
    FallingTime = 0
    CntFallingEdge = 0
    if (not IsDataOS):
        print("From {:03} To {:03} To {:03} No OD".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
        for (Index, Point) in enumerate(PointTransition[0:-1]):
            if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90")):
                RisingTime += (PointTransition[Index+1][1] - Point[1])
                CntRisingEdge += 1
                continue
            if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10")):
                FallingTime += (PointTransition[Index+1][1] - Point[1])
                CntFallingEdge += 1
                continue
        
        return (1.25 * (RisingTime / CntRisingEdge / (UnitRT/RES_Time)))
    else:
        if (Max <= 1.1*Max_Plateau):
            print("From {:03} To {:03} To {:03} OD Less Than 10% ".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
            for (Index, Point) in enumerate(PointTransition[0:-2]):
                if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90") and (PointTransition[Index+2][0] == "90")):
                    ListIndexPeak = np.where(Y_New_LPF_60Hz == np.max(Y_New_LPF_60Hz[PointTransition[Index+1][1]:PointTransition[Index+2][1]]))
                    RisingTime += (ListIndexPeak[0] - Point[1])
                    CntRisingEdge += 1
                    continue
                if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10")):
                    FallingTime += (PointTransition[Index+1][1] - Point[1])
                    CntFallingEdge += 1
                    continue
            
            return (RisingTime / CntRisingEdge / (UnitRT/RES_Time))
        else:
            print("From {:03} To {:03} To {:03} OD More Than 10% ".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
            for (Index, Point) in enumerate(PointTransition[0:-2]):
                if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90") and (PointTransition[Index+2][0] == "90")):
                    RisingTime += (PointTransition[Index+2][1] - Point[1])
                    CntRisingEdge += 1
                    continue
                if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10")):
                    FallingTime += (PointTransition[Index+1][1] - Point[1])
                    CntFallingEdge += 1
                    continue
            
            return (RisingTime / CntRisingEdge / (UnitRT/RES_Time))

# ================================================== #
# Testing Of This Module
# ================================================== #
if (__name__ == "__main__"):
    # Setting Of Sourcing Of Testing Video
    (RES_V, RES_H, RES_C) = (2436, 752, 3)
    (FPS, Duration) = (60, 8)
    (fdir_video, fname_video) = (r"D:", r"RES_{}_{}_{}_FPS_{}_GL1_{:02}_{:03}_GL2_{:02}_{:03}_GL3_{:02}_{:03}.mp4")
    lib = "FFMPEG"
    tEnd_GL1 = 10
    tEnd_GL2 = 11
    tEnd_GL3 = 20
    
    # Setting Of GUI Automation Of CA410
    targetTitle = r"PC Software for Color Analyzer"
    
    fname_MeasurementIdle = r"MeasurementIdle.png"
    fname_MeasurementWorking = r"MeasurementWorking.png"
    fname_FileSavingLevel01 = r"FileSavingLevel01.orig.png"
    fname_FileSavingLevel02 = r"FileSavingLevel02.orig.png"
    fname_FileSavingLevel03 = r"FileSavingLevel03_002.orig.png"
    
    PositionFileSavingLevel = (800, 200)
    PositionFileSavingLevel01 = None
    PositionFileSavingLevel02 = None
    PositionFileSavingLevel03 = None
    tmp = None
    
    origin = gui.position()
    
    clock.tic()
    
    for pair in pairs:
        print("\n\n\n")
        print(pair)
        
        IsODDone = False
        OD = ODStart
        TmpOD["From"] = pair[0]
        TmpOD["To"] = pair[1]
        TmpOD["OD"] = pair[0]
        TmpMPRT = 100000
        while (not IsODDone):
            before = time.time()
            
            # -------------------------------------------------- #
            # Sourcing Tesing Video
            # -------------------------------------------------- #
            if (not EnOD):
                Conditions = [[tEnd_GL1, pair[0]],
                            [tEnd_GL3, pair[1]]]
                
                if (not os.path.isfile(fdir_video + "\\" + fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[1][0], Conditions[1][1]))):
                    VideoOD(RES_V=RES_V, RES_H=RES_H, RES_C=RES_C, lib=lib,
                            FPS=FPS, Duration=Duration, Conditions=Conditions,
                            fdir=fdir_video, fname=fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[1][0], Conditions[1][1]))
            else:
                Conditions = [[tEnd_GL1, pair[0]],
                            [tEnd_GL2, np.clip(pair[1]+OD, 0, 255)],
                            [tEnd_GL3, pair[1]]]
                
                if (not os.path.isfile(fdir_video + "\\" + fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1]))):
                    VideoOD(RES_V=RES_V, RES_H=RES_H, RES_C=RES_C, lib=lib,
                            FPS=FPS, Duration=Duration, Conditions=Conditions,
                            fdir=fdir_video, fname=fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1]))
            
            # -------------------------------------------------- #
            # Displaying Testing Video
            # -------------------------------------------------- #
            fpath_video = fdir_video + "\\" + fname_video
            
            if (not EnOD):
                SP_PythonVLC = subprocess.Popen(["vlc", "--directx-device={\\.\DISPLAY1}", "--fullscreen", "--play-and-exit",
                                                fpath_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[1][0], Conditions[1][1])])
            else:
                SP_PythonVLC = subprocess.Popen(["vlc", "--directx-device={\\.\DISPLAY1}", "--fullscreen", "--play-and-exit",
                                                fpath_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1])])
            
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
            """
            CntMeasurement = 5
            while (CntMeasurement):
                try:
                    CntMeasurement -= 1
                    ActivateTargetWindow(wins, targetTitle)
                    gui.click(fname_MeasurementIdle)
                    gui.moveTo(origin)
                    time.sleep(1)
                except:
                    if (CntMeasurement == 0):
                        print("GUI Component Not Found")
                        exit()
                else:
                    break
            """
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
                print("File Smp4ng Level01 NG")
                exit()
            PositionFileSavingLevel01 = (tmp.left + int(tmp.width/2), tmp.top + int(tmp.height*5/6))
            gui.moveTo(*PositionFileSavingLevel01)
            time.sleep(1)
            
            try:
                tmp = gui.locateOnScreen(fname_FileSavingLevel02)
            except:
                print("File Smp4ng Level02 NG")
                exit()
            PositionFileSavingLevel02 = (tmp.left + int(tmp.width/2), tmp.top + int(tmp.height*1/6))
            gui.click(*PositionFileSavingLevel02)
            time.sleep(0.5)
            
            try:
                tmp = gui.locateOnScreen(fname_FileSavingLevel03)
            except:
                print("File Smp4ng Level01 NG")
                exit()
            PositionFileSavingLevel03 = (tmp.left + int(tmp.width/2), tmp.top + int(tmp.height*5/6) - 25)
            gui.moveTo(*PositionFileSavingLevel03)
            gui.doubleClick()
            time.sleep(0.5)
            if (not EnOD):
                gui.write((fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[1][0], Conditions[1][1])).replace("mp4", "csv"))
            else:
                gui.write((fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1])).replace("mp4", "csv"))
            time.sleep(0.5)
            gui.press("enter")
            time.sleep(3)
            
            #after = time.time()
            
            #print(f"Elapsed {after-before}")
            
            # -------------------------------------------------- #
            # Determining Whether IsODDone
            # -------------------------------------------------- #
            if (not EnOD):
                IsODDone = True
            else:
                if ((OD < ODEnd) and (not (Conditions[1][1] == 255))):
                    if (EnODAutoOptimize):
                        Tmp = CalcMPRT(fname=(fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1])).replace("mp4", "csv"))
                        print("From GL{:03} To GL{:03} W/I OD {:02}: MPRT = {}".format(Conditions[0][1], Conditions[1][1], Conditions[2][1], Tmp))
                        if (TmpMPRT > Tmp):
                            TmpMPRT = Tmp
                            OD = np.clip(OD + ODStep, 0, 255)
                        else:
                            TmpOD["From"] = Conditions[0][1]
                            TmpOD["To"] = Conditions[2][1]
                            TmpOD["OD"] = Conditions[1][1]
                            TmpOD["MPRT"] = TmpMPRT
                            ODTable.append(TmpOD.copy())
                            IsODDone = True
                    else:
                        OD = np.clip(OD + ODStep, 0, 255)
                else:
                    Tmp = CalcMPRT(fname=(fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1])).replace("mp4", "csv"))
                    print("From GL{:03} To GL{:03} W/I OD {:02}: MPRT = {}".format(Conditions[0][1], Conditions[1][1], Conditions[2][1], Tmp))
                    if (TmpMPRT > Tmp):
                        TmpMPRT = Tmp
                    
                    TmpOD["From"] = Conditions[0][1]
                    TmpOD["To"] = Conditions[2][1]
                    TmpOD["OD"] = Conditions[1][1]
                    TmpOD["MPRT"] = TmpMPRT
                    ODTable.append(TmpOD.copy())
                    IsODDone = True
            
            after = time.time()
            
            print(f"Elapsed {after-before}")
    
    MinimizeTargetWindow(wins, targetTitle)
    print("Measurement Done!")
    
    for ElementOD in ODTable:
        print(ElementOD)
    
    clock.toc()
    