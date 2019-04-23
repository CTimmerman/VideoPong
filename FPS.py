# https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
import datetime

now = datetime.datetime.now

class FPS:
	def __init__(self):
		self._start = None
		self._end = None
		self._numFrames = 0

	def start(self):
		self._start = now()
		return self

	def stop(self):
		self._end = now()

	def update(self):
		self._numFrames += 1

	def elapsed(self):
		return ((self._end or now()) - self._start).total_seconds()

	def fps(self):
		return self._numFrames / (self.elapsed() or .1)