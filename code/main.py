import libardrone
import cv2
import traceback
import numpy 
import camShiftClass 
import circleDetectorClass 
import droneDummy
import os
import pygame
from PIL import Image

MAX_SPEED_FWD = 0.1
MAX_SPEED_ROT = 0.8

# Use webcam as video source and dummyDrone object with logging as output device
debugMode = False

# tracking a relatively bright region or a region with a certain color
follow_light = False

# use openCV 3 instead of oc openCV 2
useOpenCV3 = False

if debugMode:
	webcamCapture = cv2.VideoCapture(0)

def perform_manual_intervention(stage, running, flying):
	return_to_hover = False
	keyPressed = True
	key = cv2.waitKey(400)
   
	if (key==-1):
		keyPressed = False
	if key == 1048603 or key == 27:  # esc
		if flying:
			drone.land()
		cv2.destroyAllWindows()
		running = False
	if key == ord('p'):
		drone.reset()
	if not flying:
		if key == 1048608 or key==ord(' '):
			
			drone.takeoff()
			drone.hover()
			
			
			flying = True
		elif key == 1048695 or key==ord('w'):
			if stage ==0 :
				stage = 1
			if stage==1 or stage==2 :
				stage=0
		elif key == ord('c'):
			stage = 0
	else:
		if key == 1048608 or key==ord(' '):
			drone.hover()
			drone.land()
			flying = False
		elif key == 1048674 or key==ord('b'):
			return_to_hover = True
			drone.move_forward()
		elif key == 1048673 or key==ord('a'):
			return_to_hover = True
			drone.move_left()
		elif key == 1048691 or key==ord('s'):
			return_to_hover = True
			drone.move_backward()
		elif key == 1048676 or key==ord('d'):
			return_to_hover = True
			drone.move_right()
		elif key == 1048689 or key==ord('q'):
			return_to_hover = True
			drone.turn_left()
		elif key == 1048677 or key==ord('e'):
			return_to_hover = True
			drone.turn_right()
		elif key == 1113938 or key==2490368:  # up
			return_to_hover = True
			drone.move_up()
		elif key == 1113940 or key==2621440:  # down
			return_to_hover = True
			drone.move_down()
		elif key == 1048625 or key==ord('1'):
			drone.speed = 0.1
		elif key == 1048626 or key==ord('2'):
			drone.speed = 0.3
		elif key == 1048627 or key==ord('3'):
			drone.speed = 0.5
		elif key == 1048628 or key==ord('4'):
			drone.speed = 0.9
		elif key == 1048695 or key==ord('w'):
			
			stage = 1
		elif key == ord('c'):
			stage = 0
		else:
			if return_to_hover:
				return_to_hover = False
				drone.hover()
	
	return keyPressed, stage, running, flying

	
def fly():
    print("fly yes")
    #drone.reset()
    running = True
    flying = False
    stage = 0 #stages: 0=hover, 1=find circle, 1=use camshift   
    print ("stage=", stage)
    #variables for the circle detector
    counter,centerX,centerY, radius, inbox_width_and_height, initialEdgeLength = 0,0,0,0,0,0  
    windowHeight, windowWidth, max_ratio_window_with_to_edge, diffX_max, diffY_max, windowCenterX, windowCenterY = 480, 640, 1, 320, 240, 320, 240

    while running:
	print("stage=",stage)
        keyPressed, stage, running, flying = perform_manual_intervention(stage, running, flying)
		# manual key command overwrite all following drone commands!

        frame = get_frame()
        
        if (frame != None):
            if (keyPressed == False):
                if (stage==1):
                    (success,frame,counter,centerX,centerY,radius,inbox_width_and_height) = circleDetectorClass.detectCircle(counter,frame,centerX,centerY,radius)
					
                    if success:
                        stage = 2
                        initialEdgeLength = inbox_width_and_height
                        windowHeight = frame.shape[1]
                        windowWidth = frame.shape[0]
                        diffX_max = windowWidth/2
                        diffY_max = windowHeight/2
                        max_ratio_window_with_to_edge = windowHeight / initialEdgeLength
						
                        print "Initialize Camshift"
                        camShiftHandler = camShiftClass.CamShift(centerX,centerY,inbox_width_and_height,inbox_width_and_height,frame, follow_light, useOpenCV3)
						
                        print "go to stage 2"
                        success, frame, centerPtX, centerPtY, minWidth = camShiftHandler.performCamShift(frame)
                elif (stage==2):  
		    print("stage =2")                  
                    success, frame, centerPtX, centerPtY, minWidth = camShiftHandler.performCamShift(frame)
                    currentEdgeLength = minWidth
                    edgeLengthRatio = currentEdgeLength/initialEdgeLength #if object is farer away than at the starting time, then the ratio is > 0
                    cv2.putText(frame, "Size ratio: " + str(edgeLengthRatio), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
					
					# steering based on camShift output
                    if success:
						#left/right
                        if centerPtX < windowCenterX -50 :
                            ratio_normalized = (windowCenterX-centerPtX/diffX_max)
                            #drone.speed = MAX_SPEED_ROT * ratio_normalized
			    return_to_hover = True
                            drone.turn_left()
			    j=0
			    while j<7000 :
				j=j+1

			    print("turn left")
                        elif centerPtX > windowCenterX + 50:
                            ratio_normalized = (centerPtX-windowCenterX/diffX_max)
                            #drone.speed = MAX_SPEED_ROT * ratio_normalized
			    return_to_hover = True
                            drone.turn_right()
			    print("turn right")
			    j=0
			    while j<7000 :
				j=j+1
							
                        #forward/backward
                        if (edgeLengthRatio > 1.2):
                            ratio_normalized = (edgeLengthRatio-1)/(max_ratio_window_with_to_edge-1)
                            #drone.speed = MAX_SPEED_FWD * ratio_normalized * 0.3
			    return_to_hover = True
                            drone.move_backward()
                            drone.hover()
			    print("backward")
			    j=0
			    while j<7000 :
				j=j+1
                        elif (edgeLengthRatio < 0.9):
                            ratio_normalized = 1 - edgeLengthRatio
                            #drone.speed = MAX_SPEED_FWD * ratio_normalized * 1
			    return_to_hover = True
                            drone.move_forward()
			    print("forward")
			    j=0
			    while j<7000 :
				j=j+1
                        else:
                            drone.hover()
			    print("hover")
                    else:
                        drone.hover()

            show_frame(frame)
 

		
def show_frame(frame):
    try:
	        		
		cv2.putText(frame, "Press 'x' to go to circleDetection: ", (170,450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0))
		cv2.imshow('Drone', frame)
    except Exception, ex:
        print "Image showing failed", ex
#*****************
def get_frame():
    W, H = 320, 240
    clock = pygame.time.Clock()
    running = True
    
    try:
            surface = pygame.image.fromstring(drone.image, (W, H), 'RGB')
            
	    

	    pygame.image.save(surface,'temp.png')

	    frame=cv2.imread('temp.png',1)
	    
            return frame
    
    except:
            pass

    

#*****************

		
if __name__ == '__main__':
	pygame.init()
	if debugMode :
		drone = droneDummy.Drone()
	else:
		drone = libardrone.ARDrone() #no HD video

	try:
		fly()
	except Exception, e:
		print "Going down because an exception occured."
		print e
		print traceback.format_exc()
	finally:
		print "Going down on close"
		drone.land()
		cv2.destroyAllWindows()




