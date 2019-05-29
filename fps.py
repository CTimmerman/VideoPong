# Based on https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
from time import sleep, time
#import pause

class FPS:
	def __init__(self, limit=144):
		self.limit = limit
		self._start = None
		self._end = None
		self._numFrames = 0
		self._period = 1.0/limit

	def elapsed(self):
		return (self._end or time()) - self._start

	def fps(self):
		return self._numFrames / (self.elapsed() or .1)
	
	def sleep(self):
		delay = self._last_mod + self._period - time() - 0.0016689
		if delay > 0:
			#pause.seconds(delay)  # 60.08
			#sleep(0.016)
			sleep(delay)  # 60.03
		#while time() < (self._last_mod + self._period):
		#	sleep(0.0001)
			#pause.milliseconds(10)

	def start(self):
		self._start = time()
		return self

	def stop(self):
		self._end = time()

	def update(self):
		self._numFrames += 1
		self._last_mod = time()
