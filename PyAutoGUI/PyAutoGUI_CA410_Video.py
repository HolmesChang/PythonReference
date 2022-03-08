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
import matplotlib.pyplot as plt

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
Pattern = "OD" #"GTG", "OD", "DGM", "Single"
if ((Pattern == "GTG") or (Pattern == "OD")):
    for GL1 in np.append(np.arange(0, 255, 48), 255):
        for GL2 in np.append(np.arange(GL1, 255, 48), 255):
            tmp = []
            if (GL2 == GL1):
                continue
            
            tmp.append(GL1)
            tmp.append(GL2)
            pairs.append(tmp)
elif (Pattern == "DGM"):
    for GL1 in np.append(np.arange(0, 255, 8), 254):
        tmp = []
        tmp.append(GL1)
        tmp.append(GL1+1)
        pairs.append(tmp)
elif (Pattern == "Single"):
    pairs = [[192, 193]]

EnOD = True
EnODAutoOptimize = True
IsODRisingDone = False
IsODFallingDone = False
ODStartRising = -8
ODStepRising = 2
ODEndRising = 32
ODStartFalling = +8
ODStepFalling = -2
ODEndFalling = -32
ODUpperLimit = 288
ODLowerLimit = 0
FactorRising = 1
FactorFalling = 1
MPRTRisingLocalMinCntLimit = 2
MPRTFallingLocalMinCntLimit = 2
TmpOD = {}
TmpOD["From"] = 0
TmpOD["To"] = 0
TmpOD["OD"] = 0
ODTable = []
ODCriterion = 1.05

RES_V = 2436
RES_H = 752
RES_C = 3
imgtest = np.zeros((RES_V, RES_H, RES_C), dtype=np.uint8)
imgR = np.empty((RES_V, RES_H, RES_C), dtype=bool)
imgG = np.empty((RES_V, RES_H, RES_C), dtype=bool)
imgB = np.empty((RES_V, RES_H, RES_C), dtype=bool)
imgR[:] = False
imgG[:] = False
imgB[:] = False
for i in np.arange(0, RES_V, 2):
    for j in np.arange(0, RES_H, 4):
        if ((i%2) == 0):
            imgR[i, j, 2] = True
            imgR[i, j+1, 1] = True
            imgR[i, j+2, 0] = True
            
            imgG[i, j, 1] = True
            imgG[i, j+1, [0, 2]] = True
            imgG[i, j+2, 1] = True
            imgG[i, j+3, [0, 2]] = True
            
            imgB[i, j, 0] = True
            imgB[i, j+2, 2] = True
            imgB[i, j+3, 1] = True
        else:
            imgB[i, j, 2] = True
            imgB[i, j+1, 1] = True
            imgB[i, j+2, 0] = True
            
            imgG[i, j, 1] = True
            imgG[i, j+1, [0, 2]] = True
            imgG[i, j+2, 1] = True
            imgG[i, j+3, [0, 2]] = True
            
            imgR[i, j, 0] = True
            imgR[i, j+2, 2] = True
            imgR[i, j+3, 1] = True

RES_Time = 0.00001
tFrame = 0.016667 #0.016667 #0.033333
UnitRT = 0.001

# ================================================== #
# Declaration ANd Definition Of This Module Function
# ================================================== #
def VideoOD (fdir: str="", fname: str="",
             RES_V: int=None, RES_H: int=None, RES_C: int=None,
             FPS: int=60, Duration: int=3,
             Conditions: List[List[np.uint8]]=[], lib: str="OpenCV",
             EnImageHalfToning: bool=False, GLLowerLimit: int=0, GLUpperLimit: int=192):
    width = RES_H 
    height = RES_V
    channel = RES_C

    fps = FPS
    sec = Duration
    
    #print("StreamGL:")
    #for Condition in Conditions:
    #    print(Condition)
    
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
        codec = "libx264"
        if (fname[-3::] == "avi"):
            codec = "rawvideo"
        
        writer = skvideo.io.FFmpegWriter(fdir + "\\" + fname,
                                         inputdict={'-r': str(fps), '-s':'{}x{}'.format(width, height), '-pix_fmt': 'rgb24'},
                                         outputdict={
                                            '-r': str(fps),
                                            '-vcodec': codec,  #use the h.264 codec #'libx264' #'rawvideo'
                                            '-pix_fmt': 'rgb24',
                                            '-crf': '0',           #set the constant rate factor to 0, which is lossless
                                            '-preset':'ultrafast'   #the slower the better compression, in princple, try #veryslow #fast #ultrafast
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

def ActivateTargetWindow (wins, targetTitle, wait=0.5):
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

def CalcMPRT (fdir: str=r"D:\Project\2D AMOLED Display Technology\Algorithm\DIQ\Experiment\Sample_001_Center_20220307_OD_W_60Hz_ODCriterion_{}_ODFrameWork".format(ODCriterion),
              fname: str="", RES_Time: np.float64=0.00001, tFrame: np.float64=0.016667, UnitRT: np.float64=0.001, Thres: np.float64=0.0025, Method: str="Median", Conditions: List[List[np.uint8]]=[]):
    if (fname == ""):
        print("Please Input Correct File Name")
        return None
    
    CntParsingFile = 5
    while (not os.path.isfile(fdir+ "\\" + fname)):
        if (CntParsingFile == 0):
            print("File Parsing Error. Exiting.")
            exit()
        
        print("{} Not Found".format((fdir+ "\\" + fname)))
        CntParsingFile -= 1
        time.sleep(1)
    
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
        if (Plateau[1] < tFrame*100000):
            Y_New_Diff[Plateau[0]:np.sum(Plateau)] = Thres
    
    Min_Plateau = np.min((Y_New_LPF_60Hz[1::])[Y_New_Diff == 0])
    Max_Plateau = np.max((Y_New_LPF_60Hz[1::])[Y_New_Diff == 0])
    # Data Plateau/
    
    Min = np.min(Y_New_LPF_60Hz)
    Max = np.max(Y_New_LPF_60Hz)
    
    (Xc_10, Xi_10) = pyaC.zerocross1d(X_New[(len(Kernel)-1)::], Y_New_LPF_60Hz-(Min_Plateau+0.1*(Max_Plateau-Min_Plateau)), getIndices=True)
    (Xc_90, Xi_90) = pyaC.zerocross1d(X_New[(len(Kernel)-1)::], Y_New_LPF_60Hz-(Min_Plateau+0.9*(Max_Plateau-Min_Plateau)), getIndices=True)
    
    print(f"Min_Plateau={Min_Plateau}, Max_Plateau={Max_Plateau}, Min={Min}, Max={Max}")
    
    # OverShooting Detection
    IsDataOS = False
    if (Max > Max_Plateau):
        #print("OverShooting")
        IsDataOS = True
        (Xc_OS_90, Xi_OS_90) = pyaC.zerocross1d(X_New[(len(Kernel)-1)::], Y_New_LPF_60Hz-(Min_Plateau+1.1*(Max_Plateau-Min_Plateau)), getIndices=True)
    # OverShooting Detection/
    
    # UnderShooting Detection
    IsDataUS = False
    if (Min < Min_Plateau):
        #print("UnderShooting")
        IsDataUS = True
        (Xc_US_10, Xi_US_10) = pyaC.zerocross1d(X_New[(len(Kernel)-1)::], Y_New_LPF_60Hz-(Min_Plateau-0.1*(Max_Plateau-Min_Plateau)), getIndices=True)
    # UnderShooting Detection/
    
    PointTransition = []
    for x in Xi_10:
        PointTransition.append(("10", x+1))
    for x in Xi_90:
        PointTransition.append(("90", x+1))
    if (IsDataOS):
        for x in Xi_OS_90:
            PointTransition.append(("OS", x+1))
    if (IsDataUS):
        for x in Xi_US_10:
            PointTransition.append(("US", x+1))
    PointTransition.sort(key=lambda x: x[1])
    
    # Debugging
    for Point in PointTransition:
        print(Point)
    
    RisingTime = 0
    CntRisingEdge = 0
    FallingTime = 0
    CntFallingEdge = 0
    if ((not IsDataOS) and (not IsDataUS)):
        print("From {:03} To {:03} To {:03} No OverShooting".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
        print("From {:03} To {:03} To {:03} No UnderShooting".format(Conditions[2][1], Conditions[3][1], Conditions[4][1]))
        for (Index, Point) in enumerate(PointTransition[0:-1]):
            if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90")):
                RisingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                CntRisingEdge += 1
                continue
            if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10")):
                FallingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                CntFallingEdge += 1
                continue
        
        return ((1 * (RisingTime / CntRisingEdge / (UnitRT/RES_Time))), (1 * (FallingTime / CntFallingEdge / (UnitRT/RES_Time))), (Max-Min_Plateau)/(Max_Plateau-Min_Plateau), (Min-Max_Plateau)/(Min_Plateau-Max_Plateau))
    elif (IsDataOS and (not IsDataUS)):
        if (Max <= (Min_Plateau+1.1*(Max_Plateau-Min_Plateau))):
            print("From {:03} To {:03} To {:03} OverShooting Less Than 10% ".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
            print("From {:03} To {:03} To {:03} No UnderShooting".format(Conditions[2][1], Conditions[3][1], Conditions[4][1]))
            for (Index, Point) in enumerate(PointTransition[0:-2]):
                try:
                    if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90") and (PointTransition[Index+2][0] == "90")):
                        ListIndexPeak = np.where(Y_New_LPF_60Hz == np.max(Y_New_LPF_60Hz[PointTransition[Index+1][1]:PointTransition[Index+2][1]]))
                        if ((ListIndexPeak[0][0]-Index) < 2*tFrame):
                            RisingTime += 1.125 * (PointTransition[Index+1][1] - Point[1]) + (ListIndexPeak[0][0] - PointTransition[Index+1][1])
                            CntRisingEdge += 1
                        else:
                            RisingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                            CntRisingEdge += 1
                        continue
                except Exception as e:
                    print(e)
                    continue
                if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10")):
                    FallingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                    CntFallingEdge += 1
                    continue
            
            return ((RisingTime / CntRisingEdge / (UnitRT/RES_Time)), (1 * (FallingTime / CntFallingEdge / (UnitRT/RES_Time))), (Max-Min_Plateau)/(Max_Plateau-Min_Plateau), (Min-Max_Plateau)/(Min_Plateau-Max_Plateau))
        else:
            print("From {:03} To {:03} To {:03} OverShooting More Than 10% ".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
            print("From {:03} To {:03} To {:03} No UnderShooting".format(Conditions[2][1], Conditions[3][1], Conditions[4][1]))
            for (Index, Point) in enumerate(PointTransition[0:-2]):
                try:
                    if ((Point[0] == "10") and (PointTransition[Index+2][0] == "OS") and (PointTransition[Index+3][0] == "OS")):
                        RisingTime += (PointTransition[Index+3][1] - Point[1])
                        CntRisingEdge += 1
                        continue
                except Exception as e:
                    print(e)
                    continue
                if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10")):
                    FallingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                    CntFallingEdge += 1
                    continue
            
            return ((RisingTime / CntRisingEdge / (UnitRT/RES_Time)), (1 * (FallingTime / CntFallingEdge / (UnitRT/RES_Time))), (Max-Min_Plateau)/(Max_Plateau-Min_Plateau), (Min-Max_Plateau)/(Min_Plateau-Max_Plateau))
    elif ((not IsDataOS) and (IsDataUS)):
        if (Min >= (Min_Plateau-0.1*(Max_Plateau-Min_Plateau))):
            print("From {:03} To {:03} To {:03} No OverShooting".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
            print("From {:03} To {:03} To {:03} UnderShooting Less Than 10%".format(Conditions[2][1], Conditions[3][1], Conditions[4][1]))
            for (Index, Point) in enumerate(PointTransition[0:-2]):
                if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90")):
                    RisingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                    CntRisingEdge += 1
                    continue
                try:
                    if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10") and (PointTransition[Index+2][0] == "10")):
                        ListIndexPeak = np.where(Y_New_LPF_60Hz == np.min(Y_New_LPF_60Hz[PointTransition[Index+1][1]:PointTransition[Index+2][1]]))
                        if ((ListIndexPeak[0][0]-Index) < 1.5*tFrame):
                            FallingTime += 1.125 * (PointTransition[Index+1][1] - Point[1]) + (ListIndexPeak[0][0] - PointTransition[Index+1][1])
                            CntFallingEdge += 1
                        else:
                            FallingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                            CntFallingEdge += 1
                        continue
                except Exception as e:
                    print(e)
                    continue
            
            return ((1 * (RisingTime / CntRisingEdge / (UnitRT/RES_Time))), (FallingTime / CntFallingEdge / (UnitRT/RES_Time)), (Max-Min_Plateau)/(Max_Plateau-Min_Plateau), (Min-Max_Plateau)/(Min_Plateau-Max_Plateau))
        else:
            print("From {:03} To {:03} To {:03} No OverShooting".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
            print("From {:03} To {:03} To {:03} UnderShooting More Than 10%".format(Conditions[2][1], Conditions[3][1], Conditions[4][1]))
            for (Index, Point) in enumerate(PointTransition[0:-2]):
                if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90")):
                    RisingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                    CntRisingEdge += 1
                    continue
                try:
                    if ((Point[0] == "90") and (PointTransition[Index+2][0] == "US") and (PointTransition[Index+3][0] == "US")):
                        FallingTime += (PointTransition[Index+3][1] - Point[1])
                        CntFallingEdge += 1
                    elif ((Point[0] == "90") and (PointTransition[Index+1][0] == "10") and (PointTransition[Index+2][0] == "10")):
                        print("Not Able To Find US Point")
                        ListIndexPeak = np.where(Y_New_LPF_60Hz == np.min(Y_New_LPF_60Hz[PointTransition[Index+1][1]:PointTransition[Index+2][1]]))
                        if ((ListIndexPeak[0][0]-Index) < 1.5*tFrame):
                            FallingTime += 1.125 * (PointTransition[Index+1][1] - Point[1]) + (ListIndexPeak[0][0] - PointTransition[Index+1][1])
                            CntFallingEdge += 1
                        else:
                            FallingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                            CntFallingEdge += 1
                    continue
                except Exception as e:
                    print(e)
                    continue
            
            return ((1 * (RisingTime / CntRisingEdge / (UnitRT/RES_Time))), (FallingTime / CntFallingEdge / (UnitRT/RES_Time)), (Max-Min_Plateau)/(Max_Plateau-Min_Plateau), (Min-Max_Plateau)/(Min_Plateau-Max_Plateau))
    else:
        for (Index, Point) in enumerate(PointTransition[0:-2]):
            # Rising
            if (Max < Max_Plateau):
                print("From {:03} To {:03} To {:03} No OverShooting".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
                if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90")):
                    RisingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                    CntRisingEdge += 1
                    continue
            elif (Max <= (Min_Plateau+1.1*(Max_Plateau-Min_Plateau))):
                print("From {:03} To {:03} To {:03} OverShooting Less Than 10% ".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
                try:
                    if ((Point[0] == "10") and (PointTransition[Index+1][0] == "90") and (PointTransition[Index+2][0] == "90")):
                        ListIndexPeak = np.where(Y_New_LPF_60Hz == np.max(Y_New_LPF_60Hz[PointTransition[Index+1][1]:PointTransition[Index+2][1]]))
                        if ((ListIndexPeak[0][0]-Index) < 1.5*tFrame):
                            RisingTime += 1.125 * (PointTransition[Index+1][1] - Point[1]) + (ListIndexPeak[0][0] - PointTransition[Index+1][1])
                            CntRisingEdge += 1
                        else:
                            RisingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                            CntRisingEdge += 1
                        continue
                except Exception as e:
                    print(e)
                    continue
            else:
                print("From {:03} To {:03} To {:03} OverShooting More Than 10% ".format(Conditions[0][1], Conditions[1][1], Conditions[2][1]))
                try:
                    if ((Point[0] == "10") and (PointTransition[Index+2][0] == "OS") and (PointTransition[Index+3][0] == "OS")):
                        RisingTime += (PointTransition[Index+3][1] - Point[1])
                        CntRisingEdge += 1
                        continue
                except Exception as e:
                    print(e)
                    continue
            # Falling
            if (Min > Min_Plateau):
                print("From {:03} To {:03} To {:03} No UnderShooting".format(Conditions[2][1], Conditions[3][1], Conditions[4][1]))
                if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10")):
                    FallingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                    CntFallingEdge += 1
                    continue
            elif (Min >= (Min_Plateau-0.1*(Max_Plateau-Min_Plateau))):
                print("From {:03} To {:03} To {:03} UnderShooting Less Than 10%".format(Conditions[2][1], Conditions[3][1], Conditions[4][1]))
                try:
                    if ((Point[0] == "90") and (PointTransition[Index+1][0] == "10") and (PointTransition[Index+2][0] == "10")):
                        ListIndexPeak = np.where(Y_New_LPF_60Hz == np.min(Y_New_LPF_60Hz[PointTransition[Index+1][1]:PointTransition[Index+2][1]]))
                        if ((ListIndexPeak[0][0]-Index) < 1.5*tFrame):
                            FallingTime += 1.125 * (PointTransition[Index+1][1] - Point[1]) + (ListIndexPeak[0][0] - PointTransition[Index+1][1])
                            CntFallingEdge += 1
                        else:
                            FallingTime += 1.25 * (PointTransition[Index+1][1] - Point[1])
                            CntFallingEdge += 1
                        continue
                except Exception as e:
                    print(e)
                    continue
            else:
                print("From {:03} To {:03} To {:03} UnderShooting More Than 10%".format(Conditions[2][1], Conditions[3][1], Conditions[4][1]))
                try:
                    if ((Point[0] == "90") and (PointTransition[Index+2][0] == "US") and (PointTransition[Index+3][0] == "US")):
                        FallingTime += (PointTransition[Index+3][1] - Point[1])
                        CntFallingEdge += 1
                        continue
                except Exception as e:
                    print(e)
                    continue
        
        return ((RisingTime / CntRisingEdge / (UnitRT/RES_Time)), (FallingTime / CntFallingEdge / (UnitRT/RES_Time)), (Max-Min_Plateau)/(Max_Plateau-Min_Plateau), (Min-Max_Plateau)/(Min_Plateau-Max_Plateau))

# ================================================== #
# Testing Of This Module
# ================================================== #
if (__name__ == "__main__"):
    # Setting Of Sourcing Of Testing Video
    (RES_V, RES_H, RES_C) = (2436, 752, 3)
    (FPS, Duration) = (60, 8)
    #(fdir_video, fname_video) = (r"D:", r"RES_{}_{}_{}_FPS_{}_GL1_{:02}_{:03}_GL2_{:02}_{:03}_GL3_{:02}_{:03}.mp4")
    (fdir_video, fname_video) = (r"D:", r"RES_{}_{}_{}_FPS_{}_GL1_{:02}_{:03}_GL2_{:02}_{:03}_GL3_{:02}_{:03}_GL4_{:02}_{:03}_GL5_{:02}_{:03}.avi")
    lib = "FFMPEG"
    tEnd_GL1 = 5
    tEnd_GL2 = 6
    tEnd_GL3 = 15
    tEnd_GL4 = 16
    tEnd_GL5 = 20
    
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
        
        IsODRisingDone = False
        IsODFallingDone = False
        ODRising = ODStartRising
        ODFalling = ODStartFalling
        TmpOD["From"] = 0
        TmpOD["To"] = 0
        TmpOD["OD"] = 0
        TmpMPRTRising = 100000
        TmpMPRTFalling = 100000
        MPRTRisingLocalMin = 0
        MPRTFallingLocalMin = 0
        MPRTRisingBuf = [100000]*3
        MPRTFallingBuf = [100000]*3
        MPRTRisingBufPointer = 0
        MPRTFallingBufPointer = 0
        while (not (IsODRisingDone and IsODFallingDone)):
            before = time.time()
            
            # -------------------------------------------------- #
            # Sourcing Tesing Video
            # -------------------------------------------------- #
            if (not EnOD):
                Conditions = [[tEnd_GL1, pair[0]],
                              [tEnd_GL2, pair[1]],
                              [tEnd_GL3, pair[1]],
                              [tEnd_GL4, pair[0]],
                              [tEnd_GL5, pair[0]]]
                
                if (not os.path.isfile(fdir_video + "\\" + fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1]))):
                    VideoOD(RES_V=RES_V, RES_H=RES_H, RES_C=RES_C, lib=lib,
                            FPS=FPS, Duration=Duration, Conditions=Conditions,
                            fdir=fdir_video, fname=fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1]),
                            EnImageHalfToning=True, GLLowerLimit=0, GLUpperLimit=192)
            else:
                Conditions = [[tEnd_GL1, pair[0]],
                              [tEnd_GL2, np.clip(pair[1]+ODRising, ODLowerLimit, ODUpperLimit)],
                              [tEnd_GL3, pair[1]],
                              [tEnd_GL4, np.clip(pair[0]+ODFalling, ODLowerLimit, ODUpperLimit)],
                              [tEnd_GL5, pair[0]]]
                
                if (not os.path.isfile(fdir_video + "\\" + fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1]))):
                    VideoOD(RES_V=RES_V, RES_H=RES_H, RES_C=RES_C, lib=lib,
                            FPS=FPS, Duration=Duration, Conditions=Conditions,
                            fdir=fdir_video, fname=fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1]),
                            EnImageHalfToning=True, GLLowerLimit=0, GLUpperLimit=192)
            
            # -------------------------------------------------- #
            # Displaying Testing Video
            # -------------------------------------------------- #
            fpath_video = fdir_video + "\\" + fname_video
            
            if (not EnOD):
                # Using VLC
                #SP_PythonVLC = subprocess.Popen(["vlc", "--directx-device={\\.\DISPLAY1}", "--fullscreen", "--play-and-exit",
                #                                fpath_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1])])
                
                # Using MPV Player
                SP_MPVPlayer = subprocess.Popen(["mpv", "--fs", "--fs-screen=1",
                                                fpath_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1])])
            else:
                # Using VLC
                #SP_PythonVLC = subprocess.Popen(["vlc", "--directx-device={\\.\DISPLAY1}", "--fullscreen", "--play-and-exit",
                #                                fpath_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1])])
                
                # Using MPV Player
                SP_MPVPlayer = subprocess.Popen(["mpv", "--fs", "--fs-screen=1",
                                                fpath_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1])])
            
            #time.sleep(1.5)
            
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
            
            CntMeasurement = 3
            while (CntMeasurement):
                try:
                    CntMeasurement -= 1
                    ActivateTargetWindow(wins, targetTitle)
                    gui.click(fname_MeasurementIdle)
                    gui.moveTo(origin)
                    #time.sleep(1)
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
            """
            
            # -------------------------------------------------- #
            # Waiting For Ending Of SubProcess
            # -------------------------------------------------- #
            #SP_PythonVLC.wait()
            SP_MPVPlayer.wait()
            #time.sleep(5)
            os.remove(fdir_video + "\\" + fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1]))
            
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
                gui.write((fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1])).replace("avi", "csv"))
            else:
                gui.write((fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1])).replace("avi", "csv"))
            time.sleep(0.5)
            gui.press("enter")
            time.sleep(3)
            
            #after = time.time()
            
            #print(f"Elapsed {after-before}")
            
            # -------------------------------------------------- #
            # Determining Whether IsODDone
            # -------------------------------------------------- #
            if (not EnOD):
                IsODRisingDone = True
                IsODFallingDone = True
            else:
                if (EnODAutoOptimize):
                    Tmp = CalcMPRT(fname=(fname_video.format(RES_V, RES_H, RES_C, FPS, Conditions[0][0], Conditions[0][1], Conditions[1][0], Conditions[1][1], Conditions[2][0], Conditions[2][1], Conditions[3][0], Conditions[3][1], Conditions[4][0], Conditions[4][1])).replace("avi", "csv"), RES_Time=RES_Time, tFrame=tFrame, Conditions=Conditions)
                    MPRTRisingBuf[int(MPRTRisingBufPointer)] = Tmp[0]
                    MPRTRisingBufPointer += 1
                    MPRTRisingBufPointer %= 3
                    MPRTFallingBuf[int(MPRTFallingBufPointer)] = Tmp[1]
                    MPRTFallingBufPointer += 1
                    MPRTFallingBufPointer %= 3
                # Checking If Rising OD Done
                if (not IsODRisingDone):
                    # Adding OD Criterion
                    if (Tmp[2] >= ODCriterion):
                        print("Rising OverShooting")
                        print(Tmp[2])
                        print(ODCriterion)
                        TmpOD["From"] = Conditions[0][1]
                        TmpOD["To"] = Conditions[2][1]
                        TmpOD["OD"] = Conditions[1][1] - ODStepRising
                        TmpOD["MPRT"] = MPRTRisingBuf[int((MPRTRisingBufPointer+2)%3)]#TmpMPRTRising
                        ODTable.append(TmpOD.copy())
                        IsODRisingDone = True
                    else:
                        if ((ODRising < ODEndRising) and (not (Conditions[1][1] == 255))):
                            if (EnODAutoOptimize):
                                print("From GL{:03} To GL{:03} W/I OD {:02}: MPRT = {}".format(Conditions[0][1], Conditions[2][1], Conditions[1][1], Tmp[0]))
                                if (TmpMPRTRising > FactorRising*Tmp[0]):
                                    TmpMPRTRising = Tmp[0]
                                    ODRising += ODStepRising
                                else:
                                    if ((MPRTRisingBuf[int((MPRTRisingBufPointer+2)%3)] > MPRTRisingBuf[int((MPRTRisingBufPointer+1)%3)]) and (MPRTRisingBuf[int((MPRTRisingBufPointer+2)%3)] > MPRTRisingBuf[int((MPRTRisingBufPointer+0)%3)])):
                                        TmpOD["From"] = Conditions[0][1]
                                        TmpOD["To"] = Conditions[2][1]
                                        TmpOD["OD"] = Conditions[1][1] - 2*ODStepRising
                                        TmpOD["MPRT"] = MPRTRisingBuf[int(MPRTRisingBufPointer)]#TmpMPRTRising
                                        ODTable.append(TmpOD.copy())
                                        IsODRisingDone = True
                                    else:
                                        TmpMPRTRising = Tmp[0]
                                        ODRising += ODStepRising
                            else:
                                ODRising += ODStepRising
                        else:
                            if (EnODAutoOptimize):
                                print("From GL{:03} To GL{:03} W/I OD {:02}: MPRT = {}".format(Conditions[0][1], Conditions[2][1], Conditions[1][1], Tmp[0]))
                                if (TmpMPRTRising > FactorRising*Tmp[0]):
                                    TmpMPRTRising = Tmp[0]
                                    TmpOD["OD"] = Conditions[1][1]
                                else:
                                    TmpOD["OD"] = Conditions[1][1] - ODStepRising
                                
                                TmpOD["From"] = Conditions[0][1]
                                TmpOD["To"] = Conditions[2][1]
                                TmpOD["MPRT"] = TmpMPRTRising
                                ODTable.append(TmpOD.copy())
                            IsODRisingDone = True
                # Check If Falling OD Done
                if (not IsODFallingDone):
                    # Adding OD Criterion
                    if (Tmp[3] >= ODCriterion):
                        print("Falling OverShooting")
                        print(Tmp[3])
                        print(ODCriterion)
                        TmpOD["From"] = Conditions[2][1]
                        TmpOD["To"] = Conditions[4][1]
                        TmpOD["OD"] = Conditions[3][1] - ODStepFalling
                        TmpOD["MPRT"] = MPRTFallingBuf[int((MPRTFallingBufPointer+2)%3)] #TmpMPRTFalling
                        ODTable.append(TmpOD.copy())
                        IsODFallingDone = True
                    else:
                        if ((ODFalling > ODEndFalling) and (not (Conditions[3][1] == 0))):
                            if (EnODAutoOptimize):
                                print("From GL{:03} To GL{:03} W/I OD {:02}: MPRT = {}".format(Conditions[2][1], Conditions[4][1], Conditions[3][1], Tmp[1]))
                                if (TmpMPRTFalling > FactorFalling*Tmp[1]):
                                    TmpMPRTFalling = Tmp[1]
                                    ODFalling += ODStepFalling
                                else:
                                    if ((MPRTFallingBuf[int((MPRTFallingBufPointer+2)%3)] > MPRTFallingBuf[int((MPRTFallingBufPointer+1)%3)]) and (MPRTFallingBuf[int((MPRTFallingBufPointer+2)%3)] > MPRTFallingBuf[int((MPRTFallingBufPointer+0)%3)])):
                                        TmpOD["From"] = Conditions[2][1]
                                        TmpOD["To"] = Conditions[4][1]
                                        TmpOD["OD"] = Conditions[3][1] - 2*ODStepFalling
                                        TmpOD["MPRT"] = MPRTFallingBuf[int(MPRTFallingBufPointer)] #TmpMPRTFalling
                                        ODTable.append(TmpOD.copy())
                                        IsODFallingDone = True
                                    else:
                                        TmpMPRTFalling = Tmp[1]
                                    ODFalling += ODStepFalling
                            else:
                                ODFalling += ODStepFalling
                        else:
                            if (EnODAutoOptimize):
                                print("From GL{:03} To GL{:03} W/I OD {:02}: MPRT = {}".format(Conditions[2][1], Conditions[4][1], Conditions[3][1], Tmp[1]))
                                if (TmpMPRTFalling > FactorFalling*Tmp[1]):
                                    TmpMPRTFalling = Tmp[1]
                                    TmpOD["OD"] = Conditions[3][1]
                                else:
                                    TmpOD["OD"] = Conditions[3][1] - ODStepFalling
                                
                                TmpOD["From"] = Conditions[2][1]
                                TmpOD["To"] = Conditions[4][1]
                                TmpOD["MPRT"] = TmpMPRTFalling
                                ODTable.append(TmpOD.copy())
                            IsODFallingDone = True
            
            after = time.time()
            
            print(f"Elapsed {after-before}")
    
    MinimizeTargetWindow(wins, targetTitle)
    print("Measurement Done!")
    
    if (EnOD and EnODAutoOptimize):
        for ElementOD in ODTable:
            print(ElementOD)
    
    clock.toc()
    
    if (EnOD and EnODAutoOptimize):
        RowLabel = ["{:03}".format(x) for x in np.append(np.arange(0, 255, 48), 255)]
        ColLabel = ["{:03}".format(x) for x in np.append(np.arange(0, 255, 48), 255)]
        DataODMPRT = np.empty((len(RowLabel), len(ColLabel)), dtype=object)
        DataODMPRT[:] = "N/A"
        for Record in ODTable:
            Row = RowLabel.index("{:03}".format(Record["From"]))
            Col = RowLabel.index("{:03}".format(Record["To"]))
            DataODMPRT[Row, Col] = "{:03}/{}".format(Record["OD"], float("{:.4f}".format(Record["MPRT"])))

        plt.table(cellText=DataODMPRT, rowLabels=RowLabel, colLabels=ColLabel, loc="center", rowLoc="center", colLoc="center", cellLoc="center", fontsize=30)
        plt.axis("off")
        plt.tight_layout()
        plt.show()
