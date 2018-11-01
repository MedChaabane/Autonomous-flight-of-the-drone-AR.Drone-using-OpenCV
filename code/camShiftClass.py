import numpy as np
import cv2

MIN_AREA = 400
MAX_AREA = 57000

useOpenCV3 = None
follow_light = None

def boxPoints(ret):
	if (useOpenCV3 == True):
		# if code crashes here, change useOpenCV3 property in main.py!
		return cv2.boxPoints(ret)
	else:
		# if code crashes here, change useOpenCV3 property in main.py!
		return cv2.cv.BoxPoints(ret)

class CamShift(object):
	def get_current_histogram_density(self, ret, pts):
		#cut only the part within the current tracking area
		mask = np.zeros(self.dst.shape, np.uint8)
		cv2.fillPoly(mask, [pts], (255, 255, 255))
		mask = mask/255
		masked_dst = np.multiply(self.dst,mask)
		tmp_dst = np.array(masked_dst)
		
		#get the sum of all pixel within the current tracking area
		denstity_mask_sum = masked_dst.sum()
		
		#get the density of the current tracking area
  		density = int(denstity_mask_sum/(ret[1][0]*ret[1][1]))
		
		#write debug info on image
		cv2.putText(tmp_dst, "Current Density: " + str(density), (10,120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
  		if self.initial_histogram_density != None:
  			cv2.putText(tmp_dst, "Original Density: " + str(self.initial_histogram_density), (10,70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
			
		# apply correction factor
		if self.initialArea != None:
			ratioCurrentToInitialArea = (ret[1][0]*ret[1][1]) / self.initialArea
			if ratioCurrentToInitialArea < 1:
				density = density *(1+ 1.5*(1-ratioCurrentToInitialArea)) #correction factor: if the square is farther away, the density usually decreases 
		
		cv2.imshow("masked histogram",tmp_dst)
		return density

	def __init__(self,c,r,w,h,initialCamImage,tmp_follow_light,tmp_useOpenCV3):
		global useOpenCV3
		useOpenCV3 = tmp_useOpenCV3
		
        # follow a relatively bright object or a object with a certain color
		global follow_light
		follow_light = tmp_follow_light
             
		# take first frame of the video
		self.frame = initialCamImage

		# setup initial location of window
		self.track_window = (int(c),int(r),int(w),int(h))

		# set up the ROI for tracking
		self.roi = self.frame[r:r+h, c:c+w]
		self.hsv_roi =  cv2.cvtColor(self.roi, cv2.COLOR_BGR2HSV)
		self.mask = cv2.inRange(self.hsv_roi, np.array((0., 60.,32.)), np.array((180.,256.,256.)))
		
		if follow_light:
			self.roi_hist = cv2.calcHist([self.hsv_roi],[2],self.mask,[256],[0,256])
		else:
			self.roi_hist = cv2.calcHist([self.hsv_roi],[0],self.mask,[180],[0,180])
		
		cv2.normalize(self.roi_hist,self.roi_hist,0,255,cv2.NORM_MINMAX)

		# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
		self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

		self.middleX = 0
		self.middleY = 0

		self.skip_commands = False
		self.initial_histogram_density = None
		self.pts = None
		self.ret = None
		self.meanHue = None
		self.isFirstTime = True
		self.initialArea = None

	def performCamShift(self, camImage):

		if camImage != None and camImage != []:
			self.hsvImage = cv2.cvtColor(camImage, cv2.COLOR_BGR2HSV)
			if follow_light:
				self.dst = cv2.calcBackProject([self.hsvImage],[2],self.roi_hist,[0,256],1)
			else:
				#follow color
				self.dst = cv2.calcBackProject([self.hsvImage],[0],self.roi_hist,[0,180],1)

			cv2.imshow("histo",self.dst)

			# apply meanshift to get the new location
			tmp_ret, tmp_track_window = cv2.CamShift(self.dst, self.track_window, self.term_crit)
			tmp_pts = boxPoints(tmp_ret)
			tmp_pts = np.int0(tmp_pts)

			# calculate density and with/length ratio of current tracking window
			if self.isFirstTime:
				self.initial_histogram_density = self.get_current_histogram_density(tmp_ret, tmp_pts)
				self.initialArea = tmp_ret[1][0]*tmp_ret[1][1]
				self.isFirstTime = False
				current_histogramm_density = self.initial_histogram_density
				current_length_width_ratio = 1
			else:
				current_histogramm_density = self.get_current_histogram_density(self.ret, self.pts)
				if tmp_ret[1][1] != 0:
					current_length_width_ratio = tmp_ret[1][0]/float(tmp_ret[1][1])
				else:
					current_length_width_ratio = 0
			
			# try to determine if camshift lost our object
			area =(tmp_ret[1][0]*tmp_ret[1][1])
			if area > MIN_AREA and area < MAX_AREA:# self.initial_histogram_density*0.2 < current_histogramm_density and area > 2500:# and current_length_width_ratio > 0.5 and current_length_width_ratio < 2:# and ratio_lastWH_and_currentWH > 0.5 and ratio_lastWH_and_currentWH < 2:
				# decision criteria can be made stricter by commenting in the other conditions
				
				self.ret = tmp_ret
				self.track_window = tmp_track_window
				self.pts = tmp_pts
				self.border_color = (0,255,0)
				success = True
			else:
				# discard tmp_pts
				self.border_color = (255,0,0) # used to print old tracking window in different color
				success = False

			
			if self.pts != None:
				self.img2 = camImage.copy()

				# Draw rectangle on image
				cv2.polylines(self.img2, [self.pts], True, self.border_color, 2)

				# Draw middlepunkt on image
				self.middleX = int(self.ret[0][0])
				self.middleY = int(self.ret[0][1])
				cv2.circle(self.img2,(self.middleX, self.middleY), 2, (10,255,255))
				return success, self.img2, self.middleX, self.middleY, min(self.ret[1][0], self.ret[1][1])
			else:
				return False, camImage, 0, 0, 0

		else:
			print 'No cam Image'
	 
	def close(self):
	 	cv2.destroyAllWindows()