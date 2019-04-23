# Based on https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
from threading import Thread
import cv2

class Camera:
	def __init__(self, src=0):
		self.stream = cv2.VideoCapture(src)
		self.grabbed, self.frame = self.stream.read()
		self.stopped = False

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		"""On unplug, cv2 prints stuff like: [ WARN:0] videoio(MSMF): can't grab frame. Error: -2147483638
		instead of throwing an error. Also, frame is None when grabbed is False, so grabbed appears to be useless."""
		while True:
			if self.stopped: return
			self.grabbed, self.frame = self.stream.read()

	def read(self):
		return self.grabbed, self.frame

	def stop(self):
		self.stopped = True