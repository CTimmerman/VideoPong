# Based on https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
from threading import Thread
from time import sleep

import cv2


class Camera:
	def __init__(self, src=0, mirror=False):
		self.mirror = mirror
		self.src = src
		self.stream = cv2.VideoCapture(src)
		self.grabbed, frame = self.stream.read()
		self.frame = cv2.flip(frame, 1) if self.mirror else frame
		self.width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
		self.fps = self.stream.get(cv2.CAP_PROP_FPS)
		self.video = None
		self.stopped = False
		self.frame_count = 0  #cap.stream.get(cv2.CAP_PROP_FRAME_COUNT) is always 0! https://github.com/opencv/opencv/issues/12091

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		"""On unplugging the USB webcam, cv2 prints stuff like
		"[ WARN:0] videoio(MSMF): can't grab frame. Error: -2147483638"
		instead of throwing an error:

		OK? True True True
		<unplug>
		OK? True True True
		[ WARN:1] videoio(MSMF): OnReadSample() is called with error status: -1072873822
		[ WARN:1] videoio(MSMF): async ReadSample() call is failed with error status: -1072873822
		[ WARN:2] videoio(MSMF): can't grab frame. Error: -1072873822
		OK? False False True
		[ WARN:2] terminating async callback
		OK? False False False
		OK? False False False
		OK? False False False
		OK? False False False
		OK? False False False
		OK? False False False
		OK? False False False
		<replug>
		OK? False False False
		OK? False False False
		OK? False False False
		OK? False False False
		OK? True True True
		OK? True True True
		"""
		while True:
			if self.stopped: return
			self.grabbed, frame = self.stream.read()  # Frame is None when grabbed is False, so grabbed appears to be useless.
			#print("OK?", self.grabbed, frame is not None, self.stream.isOpened())
			if self.grabbed:
				self.frame = cv2.flip(frame, 1) if self.mirror else frame
				if self.video:
					self.video.write(self.frame)
				self.frame_count += 1
			elif not self.stream.open(self.src):
				sleep(1)

	def read(self):
		return self.grabbed, self.frame

	def record(self, filename='cam.avi', fourcc='XVID'):
		self.video = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*fourcc), self.fps, (self.width, self.height))

	def record_stop(self):
		if self.video:
			self.video.release()
			self.video = None

	def stop(self):
		self.stopped = True
		self.record_stop()
