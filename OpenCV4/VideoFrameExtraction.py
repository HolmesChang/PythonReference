import cv2
 
# Opens the Video file
cap = cv2.VideoCapture(r"D:\RES_2436_752_3_FPS_60_GL1_10_000_GL2_11_198_GL3_20_192.mp4")
i=0
while (cap.isOpened()):
    (ret, frame) = cap.read()
    
    if (ret == False):
        break
    
    cv2.imwrite(r"D:\Frame{:03}.bmp".format(i), frame)
    i+=1
 
cap.release()
cv2.destroyAllWindows()