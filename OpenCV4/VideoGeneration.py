import os
from typing import List
import numpy as np
import cv2

def VideoOD (fdir: str="", fname: str="",
             RES_V: int=None, RES_H: int=None, RES_C: int=None,
             FPS: int=60, Duration: int=3,
             Conditions: List[np.uint8]=[]):
    width = RES_H
    hieght = RES_V
    channel = RES_C

    fps = FPS
    sec = Duration
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    video = cv2.VideoWriter(fdir + "\\" + fname, fourcc, float(fps), (width, hieght))

    img = np.zeros((RES_V, RES_H, RES_C), dtype=np.uint8)

    #Period = 0
    #for Condition in Conditions:
    #    Period += Condition[0]
    Period = Conditions[-1][0]
    print(Conditions)
    print(Period)

    for frame_count in range(fps * sec):
        remainder = frame_count % Period
        for Condition in Conditions:
            if (remainder < Condition[0]):
                img[:] = Condition[1]
                video.write(img.copy())
                break

    video.release()

if (__name__ == "__main__"):
    width = 752
    hieght = 2436
    channel = 3

    fps = 60
    sec = 10

    # Syntax: VideoWriter_fourcc(c1, c2, c3, c4) # Concatenates 4 chars to a fourcc code
    #  cv2.VideoWriter_fourcc('M','J','P','G') or cv2.VideoWriter_fourcc(*'MJPG)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # FourCC is a 4-byte code used to specify the video codec.
    # A video codec is software or hardware that compresses and decompresses digital video. 
    # In the context of video compression, codec is a portmanteau of encoder and decoder, 
    # while a device that only compresses is typically called an encoder, and one that only 
    # decompresses is a decoder. Source - Wikipedia
    #fourcc = cv2.VideoWriter_fourcc(*"DIVX")
    
    #Syntax: cv2.VideoWriter( filename, fourcc, fps, frameSize )
    video = cv2.VideoWriter('OD_W000_W255_W192.mp4', fourcc, float(fps), (width, hieght))

    img = np.zeros((2436, 752, 3), dtype=np.uint8)
    img1 = img.copy()
    img2 = img.copy(); img2[:] = 192
    img3 = img.copy(); img3[:] = 255

    for frame_count in range(int(fps*sec/2)):
        #if ((frame_count % 2) == 0):
        #    img[:] = 0
        #else:
        #    img[:] = 255
        #
        #video.write(img.copy())

        #if ((frame_count % 2) == 0):
        #    video.write(img1
        #else:
        #    video.write(img2)
        if ((frame_count % 30) < 15):
            video.write(img1)
        elif ((frame_count % 30) == 15):
            video.write(img3)
        else:
            video.write(img2)

    video.release()