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
import cv2
import skvideo.io

# ================================================== #
# Importation Of Self Development Module
# ================================================== #

# ================================================== #
# Declaration AND Definition Of This Module Variable
# ================================================== #

clock = TicToc()

# ================================================== #
# Declaration ANd Definition Of This Module Function
# ================================================== #

def VideoDynamicEdge (
    fdir: str=".", fname: str="Tmp.avi",
    RES_V: int=0, RES_H: int=0, RES_C: int=0,
    FPS: np.float64=0, Duration: np.float64=0, CODEC: str="rawvideo",
    GL1=np.array([0, 0, 0]), GL2=np.array([0, 0, 0]), Step: int=0, Direction: str="U2D"
):
    # -------------------------------------------------- #
    #   Switching CODEC By Parsing Extention Of Targeting
    # -------------------------------------------------- #
    if (fname[-3::] == "mp4"):
        CODEC = "libx264"
    #   Switching CODEC By Parsing Extention Of Targeting
    
    if (not isinstance(GL1, type(np.array([])))):
        GL1 = np.array(GL1)
    if (not isinstance(GL2, type(np.array([])))):
        GL2 = np.array(GL2)
    
    writer = skvideo.io.FFmpegWriter(
        fdir + "\\" + fname,
        inputdict={'-r': str(FPS), '-s':'{}x{}'.format(RES_H, RES_V), '-pix_fmt': 'rgb24'},
        outputdict={
            '-r': str(FPS),
            '-vcodec': CODEC,  #use the h.264 codec #'libx264' #'rawvideo'
            '-pix_fmt': 'rgb24',
            '-crf': '0',           #set the constant rate factor to 0, which is lossless
            '-preset':'ultrafast'   #the slower the better compression, in princple, try #veryslow #fast #ultrafast
                                #other options see https://trac.ffmpeg.org/wiki/Encode/H.264
        }
    )
    
    img = np.zeros((RES_V, RES_H, RES_C), dtype=np.uint8)
    img[:, :] = GL1
    
    EdgePosition = 0
    EdgeGL = GL2
    for frame_count in range(FPS * Duration):
        writer.writeFrame(img.copy())
        
        EdgePosition += Step
        if ((Direction == "U2D") or (Direction == "D2U")):
            if (EdgePosition >= RES_V):
                EdgePosition %= RES_V
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                else:
                    EdgeGL = GL2
            
            if (Direction == "U2D"):
                img[0:EdgePosition, :] = EdgeGL
            else:
                img[EdgePosition::, :] = EdgeGL
        if ((Direction == "L2R") or (Direction == "R2L")):
            if (EdgePosition >= RES_H):
                EdgePosition %= RES_H
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL == GL1
                else:
                    EdgeGL == GL2
            
            if (Direction == "L2R"):
                img[:, 0:EdgePosition] = EdgeGL
            else:
                img[:, EdgePosition::] = EdgeGL

    writer.close() #close the writer

# ================================================== #
# Declaration ANd Definition Of This Module Class
# ================================================== #

# ================================================== #
# Testing Of This Module
# ================================================== #
if (__name__ == "__main__"):
    clock.tic()
    
    fdir = "D:"
    fname = "DynamicEdge_{}_{}_{}_[{:03}, {:03}, {:03}]_[{:03}, {:03}, {:03}]_Step={}_FPS={}_Direction={}.avi"
    RES_V = 2436
    RES_H = 752
    RES_C = 3
    FPS = 60
    Duration = 10
    GL1 = np.array([0, 0, 0], dtype=np.uint8)
    GL2 = np.array([128, 128, 128], dtype=np.uint8)
    Step = 10
    Direction = "U2D"
    VideoDynamicEdge(
        fdir=fdir, fname=fname.format(RES_V, RES_H, RES_C, *GL1, *GL2, Step, FPS, Direction),
        RES_V=RES_V, RES_H=RES_H, RES_C=RES_C,
        FPS=FPS, Duration=Duration,
        GL1=GL1, GL2=GL2, Step=Step, Direction=Direction
    )
    
    clock.toc()
    