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
import matplotlib.image as im
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
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    img[:, :] = GL1
            
            if (Direction == "U2D"):
                img[0:EdgePosition, :] = EdgeGL
            else:
                img[(RES_V-EdgePosition)::, :] = EdgeGL
        
        if ((Direction == "L2R") or (Direction == "R2L")):
            if (EdgePosition >= RES_H):
                EdgePosition %= RES_H
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    img[:, :] = GL1
            
            if (Direction == "L2R"):
                img[:, 0:EdgePosition] = EdgeGL
            else:
                img[:, (RES_H-EdgePosition)::] = EdgeGL

    writer.close() #close the writer

def VideoDynamicEdgeOD (
    fdir: str=".", fname: str="Tmp.avi",
    RES_V: int=0, RES_H: int=0, RES_C: int=0,
    FPS: np.float64=0, Duration: np.float64=0, CODEC: str="rawvideo",
    GL1=np.array([0, 0, 0]), GL2=np.array([0, 0, 0]), OD1=np.array([0, 0, 0]), OD2=np.array([0, 0, 0]), Step: int=0, Direction: str="U2D"
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
    OD = OD1
    for frame_count in range(FPS * Duration):
        writer.writeFrame(img.copy())
        
        EdgePosition += Step
        if ((Direction == "U2D") or (Direction == "D2U")):
            if (EdgePosition >= RES_V):
                EdgePosition %= RES_V
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    OD = OD2
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    OD = OD1
                    img[:, :] = GL1
            
            if (Direction == "U2D"):
                img[0:np.clip((EdgePosition-Step), 0, RES_V), :] = EdgeGL
                img[np.clip((EdgePosition-Step), 0, RES_V):EdgePosition, :] = OD
            else:
                img[np.clip(((RES_V-EdgePosition)+Step), 0, RES_V)::, :] = EdgeGL
                img[(RES_V-EdgePosition):np.clip(((RES_V-EdgePosition)+Step), 0, RES_V), :] = OD
        
        if ((Direction == "L2R") or (Direction == "R2L")):                
            if (EdgePosition >= RES_H):
                EdgePosition %= RES_H
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    OD = OD2
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    OD = OD1
                    img[:, :] = GL1
            
            if (Direction == "L2R"):
                img[:, 0:np.clip((EdgePosition-Step), 0, RES_H)] = EdgeGL
                img[:, np.clip((EdgePosition-Step), 0, RES_H):EdgePosition] = OD
            else:
                img[:, np.clip(((RES_H-EdgePosition)+Step), 0, RES_H)::] = EdgeGL
                img[:, (RES_H-EdgePosition):np.clip(((RES_H-EdgePosition)+Step), 0, RES_H)] = OD

    writer.close() #close the writer

def VideoDynamicEdge30As60 (
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
    for frame_count in range(0, FPS * Duration, 2):
        for dummy in range(2):
            writer.writeFrame(img.copy())
        
        EdgePosition += Step
        
        if ((Direction == "U2D") or (Direction == "D2U")):            
            if (EdgePosition >= RES_V):
                EdgePosition %= RES_V
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    img[:, :] = GL1
            
            if (Direction == "U2D"):
                img[0:EdgePosition, :] = EdgeGL
            else:
                img[(RES_V-EdgePosition)::, :] = EdgeGL
        
        if ((Direction == "L2R") or (Direction == "R2L")):
            if (EdgePosition >= RES_H):
                EdgePosition %= RES_H
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    img[:, :] = GL1
            
            if (Direction == "L2R"):
                img[:, 0:EdgePosition] = EdgeGL
            else:
                img[:, (RES_H-EdgePosition)::] = EdgeGL

    writer.close() #close the writer

def VideoDynamicEdge30As60BIFull (
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
    imgBlack = np.zeros((RES_V, RES_H, RES_C), dtype=np.uint8)
    
    EdgePosition = 0
    EdgeGL = GL2
    for frame_count in range(0, FPS * Duration, 2):
        writer.writeFrame(img.copy())
        writer.writeFrame(imgBlack.copy())
        
        EdgePosition += Step
        
        if ((Direction == "U2D") or (Direction == "D2U")):            
            if (EdgePosition >= RES_V):
                EdgePosition %= RES_V
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    img[:, :] = GL1
            
            if (Direction == "U2D"):
                img[0:EdgePosition, :] = EdgeGL
            else:
                img[(RES_V-EdgePosition)::, :] = EdgeGL
        
        if ((Direction == "L2R") or (Direction == "R2L")):
            if (EdgePosition >= RES_H):
                EdgePosition %= RES_H
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    img[:, :] = GL1
            
            if (Direction == "L2R"):
                img[:, 0:EdgePosition] = EdgeGL
            else:
                img[:, (RES_H-EdgePosition)::] = EdgeGL

    writer.close() #close the writer

# Not Done
def VideoDynamicEdge30As60BIPartial (
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
    imgBlack = np.zeros((RES_V, RES_H, RES_C), dtype=np.uint8)
    
    EdgePosition = 0
    EdgeGL = GL2
    for frame_count in range(0, FPS * Duration, 2):
        writer.writeFrame(img.copy())
        writer.writeFrame(imgBlack.copy())
        
        EdgePosition += Step
        
        if ((Direction == "U2D") or (Direction == "D2U")):            
            if (EdgePosition >= RES_V):
                EdgePosition %= RES_V
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    img[:, :] = GL1
            
            if (Direction == "U2D"):
                img[0:EdgePosition, :] = EdgeGL
            else:
                img[(RES_V-EdgePosition)::, :] = EdgeGL
        
        if ((Direction == "L2R") or (Direction == "R2L")):
            if (EdgePosition >= RES_H):
                EdgePosition %= RES_H
                
                if (np.all(EdgeGL == GL2)):
                    EdgeGL = GL1
                    img[:, :] = GL2
                else:
                    EdgeGL = GL2
                    img[:, :] = GL1
            
            if (Direction == "L2R"):
                img[:, 0:EdgePosition] = EdgeGL
            else:
                img[:, (RES_H-EdgePosition)::] = EdgeGL

    writer.close() #close the writer

def VideoDynamicArbitraryInputImage (
    fdir_imgin: str="", fname_imgin: str="",
    fdir: str=".", fname: str="{}.avi",
    FPS: np.float64=0, Duration: np.float64=0, CODEC: str="rawvideo",
    Step: int=0, Direction: str="U2D"
):
    # -------------------------------------------------- #
    #   Switching CODEC By Parsing Extention Of Targeting
    # -------------------------------------------------- #
    if (fname[-3::] == "mp4"):
        CODEC = "libx264"
    #   Switching CODEC By Parsing Extention Of Targeting
    
    img = im.imread(fdir_imgin + "\\" + fname_imgin)
    (RES_V, RES_H, RES_C) = img.shape
    
    writer = skvideo.io.FFmpegWriter(
        fdir + "\\" + fname.replace("fname_imgin", fname_imgin[0:-4]),
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
    
    for frame_count in range(FPS * Duration):
        writer.writeFrame(img.copy())
        
        if (Direction == "U2D"):
            img = np.roll(img, Step, axis=0)
        
        if (Direction == "D2U"):
            img = np.roll(img, -Step, axis=0)
        
        if (Direction == "L2R"):
            img = np.roll(img, Step, axis=1)
        
        if (Direction == "R2L"):
            img = np.roll(img, -Step, axis=1)

    writer.close() #close the writer

def VideoDynamicArbitraryInputImageOD (
    fdir_imgin: str="", fname_imgin: str="",
    fdir: str=".", fname: str="{}.avi",
    FPS: np.float64=0, Duration: np.float64=0, CODEC: str="rawvideo",
    Step: int=0, Direction: str="U2D",
    ODLUT: List[List[np.uint8]]=[]
):
    # -------------------------------------------------- #
    #   Switching CODEC By Parsing Extention Of Targeting
    # -------------------------------------------------- #
    if (fname[-3::] == "mp4"):
        CODEC = "libx264"
    #   Switching CODEC By Parsing Extention Of Targeting
    
    img = im.imread(fdir_imgin + "\\" + fname_imgin)
    (RES_V, RES_H, RES_C) = img.shape
    
    writer = skvideo.io.FFmpegWriter(
        fdir + "\\" + fname.replace("fname_imgin", fname_imgin[0:-4]),
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
    
    for frame_count in range(FPS * Duration):
        writer.writeFrame(img.copy())
        
        if (Direction == "U2D"):
            imgtmp = np.roll(img, Step, axis=0)
        
        if (Direction == "D2U"):
            imgtmp = np.roll(img, -Step, axis=0)
        
        if (Direction == "L2R"):
            imgtmp = np.roll(img, Step, axis=1)
        
        if (Direction == "R2L"):
            imgtmp = np.roll(img, -Step, axis=1)
        
        for ODElement in ODLUT:
                imgtmp[(img == ODElement[0]) & (imgtmp == ODElement[1])] = ODElement[2]
        img = imgtmp.copy()

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
    fnameOD = "DynamicEdge_{}_{}_{}_[{:03}, {:03}, {:03}]_[{:03}, {:03}, {:03}]_[{:03}, {:03}, {:03}]_[{:03}, {:03}, {:03}]_Step={}_FPS={}_Direction={}.avi"
    fname30As60 = "DynamicEdge_{}_{}_{}_[{:03}, {:03}, {:03}]_[{:03}, {:03}, {:03}]_Step={}_FPS={}_Direction={}_30As60.avi"
    fname30As60BI = "DynamicEdge_{}_{}_{}_[{:03}, {:03}, {:03}]_[{:03}, {:03}, {:03}]_Step={}_FPS={}_Direction={}_30As60_BI.avi"
    RES_V = 2436
    RES_H = 752
    RES_C = 3
    FPS = 50
    Duration = 10
    GL1 = np.array([0, 0, 0], dtype=np.uint8)
    GL2 = np.array([144, 144, 144], dtype=np.uint8)
    OD1 = np.array([168, 168, 168], dtype=np.uint8)
    OD2 = np.array([2, 2, 2], dtype=np.uint8)
    Step = 10
    Direction = "U2D"
    
    """
    VideoDynamicEdge(
        fdir=fdir, fname=fname.format(RES_V, RES_H, RES_C, *GL1, *GL2, Step, FPS, Direction),
        RES_V=RES_V, RES_H=RES_H, RES_C=RES_C,
        FPS=FPS, Duration=Duration,
        GL1=GL1, GL2=GL2, Step=Step, Direction=Direction
    )
    
    VideoDynamicEdgeOD(
        fdir=fdir, fname=fnameOD.format(RES_V, RES_H, RES_C, *GL1, *OD1, *GL2, *OD2, Step, FPS, Direction),
        RES_V=RES_V, RES_H=RES_H, RES_C=RES_C,
        FPS=FPS, Duration=Duration,
        GL1=GL1, GL2=GL2, OD1=OD1, OD2=OD2, Step=Step, Direction=Direction
    )
    """
    
    VideoDynamicArbitraryInputImage(
        fdir_imgin=r"D:", fname_imgin=r"蘭亭集序002_Binary_1125x2436.bmp",
        fdir=r"D:", fname=r"{}_Step={}_FPS={}_Direction={}.avi".format("fname_imgin", Step, FPS, Direction),
        FPS=FPS, Duration=Duration,
        Step=Step, Direction="U2D"
    )
    
    VideoDynamicArbitraryInputImageOD(
        fdir_imgin=r"D:", fname_imgin=r"蘭亭集序002_Binary_1125x2436.bmp",
        fdir=r"D:", fname=r"{}_Step={}_FPS={}_Direction={}_OD.avi".format("fname_imgin", Step, FPS, Direction),
        FPS=FPS, Duration=Duration,
        Step=Step, Direction="U2D",
        ODLUT=[
            [0, 192, 224]
        ]
    )
    
    """
    VideoDynamicEdge30As60(
        fdir=fdir, fname=fname30As60.format(RES_V, RES_H, RES_C, *GL1, *GL2, Step, FPS, Direction),
        RES_V=RES_V, RES_H=RES_H, RES_C=RES_C,
        FPS=FPS, Duration=Duration,
        GL1=GL1, GL2=GL2, Step=Step, Direction=Direction
    )
    
    VideoDynamicEdge30As60BIFull(
        fdir=fdir, fname=fname30As60BI.format(RES_V, RES_H, RES_C, *GL1, *GL2, Step, FPS, Direction),
        RES_V=RES_V, RES_H=RES_H, RES_C=RES_C,
        FPS=FPS, Duration=Duration,
        GL1=GL1, GL2=GL2, Step=Step, Direction=Direction
    )
    """
    
    clock.toc()
    