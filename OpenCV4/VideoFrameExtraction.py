import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as img
import cv2

RES_V = 2436
RES_H = 752
RES_C = 3
FPS = 60
Duration = 8
GL1 = 0
tGL1 = 10
GL2 = 198
tGL2 = 11
GL3 = 192
tGL3 = 20

fname = r"D:\Test.mp4"

# Opens the Video file
cap = cv2.VideoCapture(fname.format(RES_V, RES_H, RES_C,
                                    FPS,
                                    tGL1, GL1,
                                    tGL2, GL2,
                                    tGL3, GL3))

i=0
while (cap.isOpened()):
    (ret, frame) = cap.read()
    
    if (ret == False):
        break
    
    _ = cv2.imwrite(r"D:\Frame{:03}.bmp".format(i), frame)
    i+=1

cap.release()
cv2.destroyAllWindows()

StreamGL = []
for cnt in np.arange(i):
    imgin = img.imread(r"D:\Frame{:03}.bmp".format(cnt))
    
    if (np.all(imgin == imgin[0, 0, 0])):
        StreamGL.append(imgin[0, 0, 0])

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(StreamGL, marker="o", markersize=1, linestyle="-", linewidth=0.5)
fig.show()

print(set(StreamGL))

#_ = input("Enter Any Key To Exit")
