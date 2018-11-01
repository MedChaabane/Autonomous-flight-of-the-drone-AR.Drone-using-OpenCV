import cv2
import numpy

ALLOWED_RADIUS_CHANGE = 30
ALLOWED_CENTER_SHIFT = 40
MIN_NUM_CONSECUTIVE_MATCHES = 7
MIN_RADIUS_OF_CIRCLES = 20
MIN_DISTANCE_BETWEEN_CIRCLES = 800

def detectCircle(sameCircleCounter,frameRGB, centerX, centerY, radius):
    centerX_prev = centerX
    centerY_prev= centerY
    radius_prev = radius
    inbox_width_and_height = 0

    frame = cv2.cvtColor(frameRGB, cv2.COLOR_BGR2GRAY)
    if frame != None:
        frametmp = cv2.medianBlur(frame,5)
        #find circles
            #param1: higher treshold of canny edge detector
            #param2: accumulator treshold for circle center. The smaller it is, the more small circles are detected
        circles = cv2.HoughCircles(frametmp, 3, 1, MIN_DISTANCE_BETWEEN_CIRCLES, param1=30, param2=40, minRadius = MIN_RADIUS_OF_CIRCLES, maxRadius=1000)                               
        
        radius = 0
        success = False
        if circles != None:
            
            for i in circles[0,:]:
                #draw the outer circle
                cv2.circle(frameRGB,(i[0],i[1]),i[2],(0,255,0),2)
                #draw the center of the circle
                cv2.circle(frameRGB,(i[0],i[1]),2,(0,0,255),3)

			#get inner bounding box
            if len(circles) == 1:
                circle=circles[0][0]
                radius = circle[2]
                centerX = circle[0]
                centerY = circle[1]
                inbox_width_and_height = 2* numpy.sqrt((radius**2)/2)

        #check whether the circle change is within the threshold
        if radius != 0:
            diffRadius = numpy.abs(radius-radius_prev)
            diffX=numpy.abs(centerX-centerX_prev)
            diffY= numpy.abs(centerY-centerY_prev)

            if  (diffRadius < ALLOWED_RADIUS_CHANGE) and (diffX < ALLOWED_CENTER_SHIFT) and (diffY < ALLOWED_CENTER_SHIFT):
                sameCircleCounter += 1
                print "sameCircleCounter: " + str(sameCircleCounter)
            else:
                sameCircleCounter = 0

            if sameCircleCounter > MIN_NUM_CONSECUTIVE_MATCHES:
                print "Found circle!"
                success = True

        return (success,frameRGB,sameCircleCounter,centerX,centerY,radius,inbox_width_and_height)