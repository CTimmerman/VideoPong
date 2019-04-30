# Based on https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
import datetime
from time import time, sleep

now = datetime.datetime.now

class FPS:
	def __init__(self, limit=144):
		self._start = None
		self._end = None
		self._numFrames = 0
		self.limit = limit

	def elapsed(self):
		return ((self._end or now()) - self._start).total_seconds()

	def fps(self):
		return self._numFrames / (self.elapsed() or .1)
	
	def sleep(self):
		while time() < (self._last_mod + 1 / (self.limit + 4)): sleep(0.0001)  # 1 ms is too fine for sleep, so pretend limit is higher.

	def start(self):
		self._start = now()
		return self

	def stop(self):
		self._end = now()

	def update(self):
		self._numFrames += 1
		self._last_mod = time()
