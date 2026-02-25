import cv2
import numpy as np

frameWidth = 640
frameHeight = 480
cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)
cap.set(4, frameHeight)

def empty(a):
    pass

cv2.namedWindow("parameters")
cv2.resizeWindow("parameters",640,240)
cv2.createTrackbar("Threshold1","parameters", 0,255,empty)
cv2.createTrackbar("Threshold2","parameters", 91,255,empty)
cv2.createTrackbar("Area","parameters", 5000,30000,empty)

def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width =imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range (0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0,0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank] *rows
        for x in range (0,rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0,rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0,0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0]), None, scale, scale)
            if len(imgArray[x].shape) ==2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver

def getCountours(img, imgcountour):
    countours, hiearchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in countours:
        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area","parameters")
        if area > areaMin:
            cv2.drawContours(imgcountour, countours, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt,0.02*peri, True)
            print(len(approx))
            x, y, w, h = cv2.boundingRect(approx)
            cv2.rectangle(imgCountour, (x,y), (x+w, y+h),(0,0,225),5)
            cv2.putText(imgCountour, "Points"+ str(len(approx)),(x+w+20,y+20),cv2.FONT_HERSHEY_PLAIN,.7,(255,0,0),2)
            cv2.putText(imgCountour, "Area" + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_PLAIN,.7, (255,0,0), 2)


while True:
    success, img = cap.read()
    imgCountour = img.copy()
    imgblur = cv2.GaussianBlur(img, (7,7), 1)
    imggray = cv2.cvtColor(imgblur, cv2.COLOR_BGR2GRAY)
    threshold1 = cv2.getTrackbarPos("Threshold1", "parameters")
    threshold2 = cv2.getTrackbarPos("Threshold2", "parameters")
    imgCanny = cv2.Canny(imggray,threshold1, threshold2)
    kernel = np.ones((5,5))
    imgdil = cv2.dilate(imgCanny, kernel, iterations=1)
    getCountours(imgdil, imgCountour)

    imgstack = stackImages(1,([img,imgdil,imgCountour]))

    cv2.imshow("obama", imgstack)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
