import cv2
import dlib
import time
import threading
import math
import datetime
import os
import openpyxl
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import numpy as np
from skimage import util
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage import measure
from skimage.measure import regionprops
import matplotlib.patches as patches
import sklearn
import joblib
#import trial_23


SNo = int(1)
counter = 0
sheet = {}
now = datetime.datetime.now()
carCascade = cv2.CascadeClassifier('myhaar.xml')
video = cv2.VideoCapture('nv.mp4')
WIDTH = 1280
HEIGHT = 720
def estimateSpeed(location1, location2, fps):
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    # ppm = location2[2] / carWidht
    ppm = 10                          #$$$$
    d_meters = d_pixels / ppm
    print(fps)
    speed = d_meters * 10 * 3.6 #3600/1000
    return speed
def trackMultipleObjects():
    rectangleColor = (0, 255, 0)
    frameCounter = 0
    currentCarID = 0
    fps = 1
    cropped_image = {}
    LPN = {}
    carTracker = {}
    carNumbers = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000
    counter = 0
    a = 0
    myuse = []

    while True:

        start_time = time.time()
        rc, image_2 = video.read()
        if type(image_2) == type(None):
            break
		
        image_1 = cv2.resize(image_2, (WIDTH, HEIGHT))
        resultImage = image_1.copy()
        height = image_1.shape[0]
        width = image_1.shape[1]
        image = image_1[0:height, 0:int(width/2)]
		
        frameCounter = frameCounter + 1
		
        carIDtoDelete = []

        for carID in carTracker.keys():
            trackingQuality = carTracker[carID].update(image)
			
            if trackingQuality < 7: #7
                carIDtoDelete.append(carID)
				
        for carID in carIDtoDelete:
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)
            cropped_image.pop(carID,None)
            LPN.pop(carID, None)
		
        if not (frameCounter % 10): #it goes inside only when frameCounter is a multiple of 10
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

            cars = list(cars)

            #print(cars)
            
            for i in range (len(cars)):
                #print(cars, 'HAKUNA MATATA')
                if (cars[i][0] < 195) or (cars[i][2] < 58) or (cars[i][3] < 58) or ((cars[i][1] > 40) and (cars[i][2] < 68)) or ((cars[i][1] > 268) and (cars[i][2] < 250)) or ((cars[i][1] > 268) and (cars[i][3] < 250)) :
                    myuse.append(i)

            if myuse != []:
                #print(cars)
                for i in range(len(myuse)-1, -1, -1):
                    cars.pop(myuse[i])

                #print(cars)
                myuse = []

            for i in range(len(cars)):
                if (cars[i][1] > 40) and (cars[i][2] < 70):
                    myuse.append(i)

            if myuse != []:
                #print(cars)
                for i in range(len(myuse)-1, -1, -1):
                    cars.pop(myuse[i])

                #print(cars)
                myuse = []

            for i in range(len(cars)):
                if (cars[i][1] > 110) and (cars[i][2] < 120):
                    myuse.append(i)

            if myuse != []:
                #print(cars)
                for i in range(len(myuse)-1, -1, -1):
                    cars.pop(myuse[i])

                #print(cars)
                myuse = []

            for i in range(len(cars)):
                if (cars[i][1] > 268) and (cars[i][2] < 250):
                    myuse.append(i)

            if myuse != []:
                for i in range(len(myuse)-1, -1, -1):
                    cars.pop(myuse[i])

                myuse = []
            for (_x, _y, _w, _h) in cars:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h
                matchCarID = None
                for carID in carTracker.keys():
                    trackedPosition = carTracker[carID].get_position()
                    t_x = int(trackedPosition.left())
                    t_y = int(trackedPosition.top())
                    t_w = int(trackedPosition.width())
                    t_h = int(trackedPosition.height())

                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h
                    if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                        matchCarID = carID
                if matchCarID is None:
                    print ('Creating new tracker ' + str(currentCarID))
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]

                    currentCarID = currentCarID + 1

        myuse = []
        for carID in carTracker.keys():
            x_1 = carTracker[carID].get_position().left()
            y_1 = carTracker[carID].get_position().top()
            w_1 = carTracker[carID].get_position().width()
            h_1 = carTracker[carID].get_position().height()
            for carID_2 in carTracker.keys():
                x_2 = carTracker[carID_2].get_position().left()
                y_2 = carTracker[carID_2].get_position().top()
                w_2 = carTracker[carID_2].get_position().width()
                h_2 = carTracker[carID_2].get_position().height()
                if (carID != carID_2):
                    #print(x_2, x_1+10, x_2+w_2, ' ', x_2, x_1+w_1-10, x_2+w_2, ' ', y_2, y_1+h_1+10, y_2+h_2, 'SEEE THIS BRO')
                    if (x_2 < (x_1 + 10)) and ((x_1 + 10) < (x_2 + w_2)) and ((x_1 + w_1 - 10) > x_2) and ((x_1 + w_1 - 10) < (x_2 + w_2)) and ((y_1 + h_1 + 10) > y_2) and ((y_1 + h_1 +10) < (y_2 + h_2)):
                        myuse.append(carID)

        if myuse != []:
            #print(cars)
            for i in range(len(myuse)-1, -1, -1):
                carTracker.pop(myuse[i])
                carLocation1.pop(myuse[i])
        myuse = []

        for carID in carTracker.keys():
            x_1 = carTracker[carID].get_position().left()
            y_1 = carTracker[carID].get_position().top()
            w_1 = carTracker[carID].get_position().width()
            h_1 = carTracker[carID].get_position().height()
            for carID_2 in carTracker.keys():
                x_2 = carTracker[carID_2].get_position().left()
                y_2 = carTracker[carID_2].get_position().top()
                w_2 = carTracker[carID_2].get_position().width()
                h_2 = carTracker[carID_2].get_position().height()
                if (carID != carID_2):
                    if ((x_1 + w_1 + 10) > x_2) and ((x_1 + w_1 + 10) < (x_2 + w_2)) and ((y_1 + 10) > y_2) and ((y_1 + 10) < (y_2 + h_2)) and ((y_1 + h_1 - 10) > y_2) and ((y_1 + h_1 - 10) < (y_2 + h_2)) :
                        myuse.append(carID)
        if myuse != []:
            for i in range(len(myuse)-1, -1, -1):
                carTracker.pop(myuse[i])
                carLocation1.pop(myuse[i])
        myuse = []

        for carID in carTracker.keys():
            x_1 = carTracker[carID].get_position().left()
            y_1 = carTracker[carID].get_position().top()
            w_1 = carTracker[carID].get_position().width()
            h_1 = carTracker[carID].get_position().height()
            for carID_2 in carTracker.keys():
                x_2 = carTracker[carID_2].get_position().left()
                y_2 = carTracker[carID_2].get_position().top()
                w_2 = carTracker[carID_2].get_position().width()
                h_2 = carTracker[carID_2].get_position().height()
                if (carID != carID_2):
                    if ((x_1 + 10) > x_2) and ((x_1 + 10) < (x_2 + w_2)) and ((x_1 + w_1 - 10) > x_2) and ((x_1 + w_1 - 10) < (x_2 + w_2)) and ((y_1 - 10) > y_2) and ((y_1 - 10) < (y_2 + h_2)):
                        myuse.append(carID)


        if myuse != []:
            #print(cars)
            for i in range(len(myuse)-1, -1, -1):
                carTracker.pop(myuse[i])
                carLocation1.pop(myuse[i])
        myuse = []
        for carID in carTracker.keys():
            x_1 = carTracker[carID].get_position().left()
            y_1 = carTracker[carID].get_position().top()
            w_1 = carTracker[carID].get_position().width()
            h_1 = carTracker[carID].get_position().height()
            for carID_2 in carTracker.keys():
                x_2 = carTracker[carID_2].get_position().left()
                y_2 = carTracker[carID_2].get_position().top()
                w_2 = carTracker[carID_2].get_position().width()
                h_2 = carTracker[carID_2].get_position().height()
                if (carID != carID_2):
                    if ((x_1 - 10) > x_2) and ((x_1 - 10) < (x_2 + w_2)) and ((y_1 + 10) > y_2) and ((y_1 + 10) < (y_2 + h_2)) and ((y_1 + h_1 - 10) > y_2) and ((y_1 + h_1 - 10) < (y_2 + h_2)) :
                        myuse.append(carID)


        if myuse != []:
            for i in range(len(myuse)-1, -1, -1):
                carTracker.pop(myuse[i])
                carLocation1.pop(myuse[i])
        myuse = []
        for carID in carTracker.keys():
            trackedPosition = carTracker[carID].get_position()
            t_x = int(trackedPosition.left())
            t_y = int(trackedPosition.top())
            t_w = int(trackedPosition.width())
            t_h = int(trackedPosition.height())
            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)
            carLocation2[carID] = [t_x, t_y, t_w, t_h]
        end_time = time.time()
        if not (end_time == start_time):
            fps = 1.0/(end_time - start_time)
        for i in carLocation1.keys():	
            if frameCounter % 1 == 0: #it will always work
                [x1, y1, w1, h1] = carLocation1[i]
                [x2, y2, w2, h2] = carLocation2[i]
                carLocation1[i] = [x2, y2, w2, h2]
                if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                    if (speed[i] == None or speed[i] == 0): #275.. 285  and y1 >= 250 and y1 <= 260.. this is to give command to the code to only estimate speed when the vehicle is between 275 and 285! 
                        speed[i] = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2], fps)
                        print('1st', x1, y1, w1, h1, ' ', '2nd', x2, y2, w2, h2, ' ', speed[i], ' ', 'fps:', fps)
                    if (speed[i] != None and (x2 > x1+5 or x2 < x1-5) and (y2 > y1+5 or y2 < y1-5)): #so that even if the driver opens his seat, the code doesn't detect speed in that
                        cv2.putText(resultImage, str(int(speed[i])) + " km/hr", (int(x1 + w1/2), int(y1-5)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
                        print(speed[i], 'YOOOOOOOOOOOO')
                        print(datetime.datetime.now())
                        cropped_image[i] = image[y1:y1+h1+25, x1:x1+w1+25]

        cv2.imshow('result', resultImage)
        if cv2.waitKey(33) == 27:
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    
    trackMultipleObjects()
