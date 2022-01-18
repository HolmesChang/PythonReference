import os
import numpy as np
import cv2

width = 752
hieght = 2436
channel = 3

fps = 60.764
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
video = cv2.VideoWriter('test.mp4', fourcc, float(fps), (width, hieght))

img = np.zeros((2436, 752, 3), dtype=np.uint8)
img1 = img.copy()
img2 = img.copy(); img2[:] = 255

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

    video.write(img1)
    video.write(img2)

video.release()