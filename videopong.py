# -*- coding: utf-8 -*-
"""Video Pong by Cees Timmerman

H for help, +/- to adjust ball tolerance, C captures image,
R records, V records with overlay, and Esc exits.

2019-03-25 v0.1 based on https://theailearner.com/2019/03/18/set-camera-timer-using-opencv-python/
2019-03-26 v0.2 Ball bounces off video changes.
2019-04-24 v0.3 Mirror by default and PEP 8 a bit.
2019-04-30 v0.4 Fixed mirror feature, added video recording, more uniform and efficient speed, record indicator.
2019-05-30 v0.5 Toggle recording, adjust tolerance, tweak FPS, obey window close, support webcam hotswap.
2019-06-04 v0.6 Tweak FPS, record raw footage, show help on start.
"""
from __future__ import print_function
import time

import cv2  # python -m pip install opencv-python
import numpy as np

from camera import Camera
from fps import FPS


BLACK = (0, 0, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)

def random_color():
	from random import randint as rnd
	return (rnd(0, 255), rnd(0, 255), rnd(0, 255))

def write(img, msg, x=2, y=13, size=0.5, thickness=1, color=WHITE, window_title=''):
	font = cv2.FONT_HERSHEY_SIMPLEX
	cv2.putText(img, str(msg), (x+1, y+1), font, size, BLACK, thickness, cv2.LINE_AA)  # Drop shadow for contrast.
	cv2.putText(img, str(msg), (x, y), font, size, color, thickness, cv2.LINE_AA)
	if window_title: cv2.imshow(window_title, img)

captions = []
def caption(write_args, duration=1):
	global captions, fps
	frames = int(duration * fps.fps())
	captions.append([frames, *write_args])
	print(write_args[0])

print(__doc__)

fps = FPS(60)
cap = Camera(mirror=True).start()
#TODO: bg1 = cv2.BackgroundSubtractorMOG2(history=3, nmixtures=5, backgroundRatio=0.0001)
w = cap.width or 640
h = cap.height or 480
ball_color = random_color()
r = 20
x = w//2 - r//2
y = h//2 - r//2
dx = dy = w // fps.limit // 2  # Ball crosses screen in about 2 seconds.

tolerance = 34  # Bounce at this amount of color change.
window_title = 'Video Pong'
countdown = old_frame_count = 0
img = new_img = diff = video = None
fps.start()
while True:
	old_img = new_img  # Use raw feed without overlay.
	ok, new_img = cap.read()
	if new_img is not None:
		img = new_img.copy()  # No motion blur.
		#fg1 = bg1.apply(img)
		#cv2.imshow('BG', fg1)
		#cv2.BackgroundSubtractor.apply(img)
	else:
		img = new_img = np.zeros((480, 640, 3), np.uint8)
	
	fps.update()
	
	if old_img is not None and img is not None:
		diff = cv2.absdiff(old_img, img) > tolerance

	# Handle ball.
	x += dx; y += dy
	if not (r < x < 640-r) or diff is not None and diff[y][x].any():
		dx*=-1; ball_color = random_color()
	if not (r < y < 480-r) or diff is not None and diff[y][x].any():
		dy*=-1; ball_color = random_color()
	cv2.circle(img, (x, y), r, ball_color, 2)
	
	write(img, "{:.2f} FPS".format(fps.fps()), 20, 30)

	# Handle capture.
	if countdown > 0:
		countdown -= 1
		if countdown == 0:
			path = 'cam ' + time.strftime("%Y-%m-%d %H.%M.%S") + '.jpg'
			if not cv2.imwrite(path, img):
				msg = "Could not save photo to %r" % path
			else:
				msg = "Saved image to %s" % path
			caption([msg, 20, 80, 0.6])
		else:
			write(img, str(int(countdown//fps.fps()) + 1), 250, 250, 7, 3)
	
	# Handle user input for 1 ms.
	k = cv2.waitKey(1) # Add & 0xFF for 64-bit Windows perhaps.
	if old_img is None:
		k = ord('h')
	elif cv2.getWindowProperty(window_title, 0) < 0:  # window closed
		break
	
	if k >= 0:
		k = chr(k).lower()
		if k == '+':
			tolerance += 1
			caption(["Tolerance: %s" % tolerance], 1)
		elif k == '-':
			tolerance -= 1
			caption(["Tolerance: %s" % tolerance], 1)
		elif k == 'c':  # capture
			countdown = int(3 * fps.fps())
		elif k == 'e':
			caption([fps.elapsed()])
		elif k == 'h':  # help
			for i, line in enumerate(__doc__.splitlines()):
				caption([line, 2, 55+i*14], 5)
		elif k == 'r':  # record raw video
			if cap.video:
				cap.record_stop()
			else:
				path = 'cam_' + time.strftime("%Y-%m-%d_%H.%M.%S") + '.avi'
				caption(["Recording to %s @ %s FPS" % (path, cap.fps)])
				cap.record(path)
		elif k == 'v':  # video
			if video:
				video.release()
				video = None
			else:
				path = 'cap_' + time.strftime("%Y-%m-%d_%H.%M.%S") + '.avi'
				caption(["Recording to %s @ %s FPS" % (path, fps.limit)])
				#cap.record(path)  # Lacks our overlay.
				video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'XVID'), fps.limit, (w, h))
		elif k == chr(27):  # Esc
			break
	
	# Render text.
	for i, arr in enumerate(captions.copy()):
		arr[0] -= 1
		if arr[0] <= 0: captions.remove(arr)
		write(img, *arr[1:])
	
	# Recording indicator. "•" would require pillow module.
	if cap.video: write(img, ".", w-40, 30, 4, 6, RED)
	if video: write(img, ".", w-60, 30, 4, 6, WHITE)
	
	# Show frame.
	cv2.imshow(window_title, img)
	
	# Record including overlay.
	if video:
		# The writer limits its own frames... or not.
		#frame_count = cap.frame_count
		#if (frame_count > old_frame_count) and video:
		#	old_frame_count = frame_count
		video.write(img)
	
	# Don't waste CPU cycles.
	fps.sleep()

if video: video.release()
cap.stop()
cv2.destroyAllWindows()