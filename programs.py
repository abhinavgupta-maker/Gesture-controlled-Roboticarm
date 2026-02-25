import cv2
import numpy as np

circles = np.zeros((4,2),np.int_)
counter = 0

def mousePoints(event,x,y,flags,params):
    global counter
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x,y)
        circles[counter] = x,y
        counter = counter + 1
        print(circles)

width, height = 250, 350
img = cv2.imread("images1/cards1.png")
while True:
    if counter == 4:
        pts1 = np.float32([circles[0],circles[1],circles[2],circles[3]])
        pts2 = np.float32([[0,0],[width,0],[width,height], [0, height]])
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
        output = cv2.warpPerspective(img,matrix,(width, height))
        cv2.imshow("obama", output)
    for i in range (0,4):
        cv2.circle(img,(circles[i][0],circles[i][1]), 5, (0, 0, 255),cv2.FILLED)

    cv2.imshow("Doge", img)
    cv2.setMouseCallback("Doge", mousePoints)
    cv2.waitKey(0)