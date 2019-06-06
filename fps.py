# Based on https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
from time import sleep, clock


class FPS:
	def __init__(self, limit=144):
		self.limit = limit
		self._start = None
		self._end = None
		self._last_mod = clock()
		self._frame_count = 0
		self._period = 1.0/limit

	def elapsed(self):
		return (self._end or clock()) - self._start

	def fps(self):
		return self._frame_count / (self.elapsed() or 1.0)
	
	def sleep(self):
		#delay = self._last_mod + self._period - clock() - 0.001  # 60.07 FPS  #0.0016689  # 60.3 FPS
		delay = min(self._period, (self.fps() - self.limit)+0.01)  # 60.00 FPS
		#print(delay)
		if delay > 0: sleep(delay)

	def start(self):
		self._start = clock()
		self._frame_count = 0
		return self

	def stop(self):
		self._end = clock()

	def update(self):
		self._last_mod = clock()
		self._frame_count += 1
