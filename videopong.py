# -*- coding: utf-8 -*-
"""Video Pong by Cees Timmerman

Press C to capture a screenshot, V to record, and Esc to exit.

2019-03-25 v0.1 based on https://theailearner.com/2019/03/18/set-camera-timer-using-opencv-python/
2019-03-25 v0.2 Ball bounces off video changes.
2019-04-24 v0.3 Mirror by default and PEP 8 a bit.
2019-04-30 v0.3.1 Fixed mirror feature.
2019-04-30 v0.4 Added video recording.
"""
from __future__ import print_function
import time

import cv2  # python -m pip install opencv-python

from camera import Camera
from fps import FPS


def random_color():
	from random import randint as rnd
	return (rnd(0, 255), rnd(0, 255), rnd(0, 255))

def write(img, msg, x=0, y=10, size=0.5, color=(255, 255, 255), thickness=1, window_title=''):
	font = cv2.FONT_HERSHEY_SIMPLEX
	cv2.putText(img, msg, (x+thickness, y+thickness), font, size, (0, 0, 0), thickness, cv2.LINE_AA)  # Drop shadow for contrast.
	cv2.putText(img, msg, (x, y), font, size, color, thickness, cv2.LINE_AA)
	if window_title: cv2.imshow(window_title, img)

print(__doc__)

ball_color = random_color()
r = 20
x, y = 100, 100
dx, dy = 1, 1
tolerance = 20
window_title = 'Video Pong'

#cap = cv2.VideoCapture(0)  # read() blocks.
#cap.stop = cap.release
cap = Camera(mirror=True).start()  # Nonblocking read()
#TODO: bg1 = cv2.BackgroundSubtractorMOG2(history=3, nmixtures=5, backgroundRatio=0.0001)

fps = FPS(); fps.start()
countdown = old_frame_count = 0
img = new_img = diff = video = None
while True:
	old_img = new_img  # Use raw feed without overlay.
	ok, new_img = cap.read()
	if ok:
		img = new_img.copy()  # No motion blur.
		#fg1 = bg1.apply(img)
		#cv2.imshow('BG', fg1)
		#cv2.BackgroundSubtractor.apply(img)
	else:
		print("Can't get image.")
		cap.stop()
	
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
	
	write(img, "{:.2f} FPS, frame {}".format(fps.fps(), old_frame_count), 20, 30)

	if countdown > 0:
		countdown -= 1
		if countdown == 0:
			path = 'cam ' + time.strftime("%Y-%m-%d %H.%M.%S") + '.jpg'
			if not cv2.imwrite(path, img):
				msg = "Could not save photo to %r" % path
			else:
				msg = "Saved image to %s" % path
			write(img, msg, 20, 80, 0.6, window_title=window_title)
			print(msg)
			cv2.waitKey(600)
		else:
			write(img, str(int(countdown//fps.fps()) + 1), 250, 250, 7, thickness=3)

	cv2.imshow(window_title, img)
	
	# Handle user input for 1 ms.
	k = cv2.waitKey(1) # Add & 0xFF for 64-bit Windows perhaps.
	if k == ord('c'):
		countdown = int(3 * fps.fps())
	if k == ord('v'):
		if video:
			write(img, "Already recording.", window_title=window_title)
			cv2.waitKey(200)
			#print(video.getBackendName())
		else:
			path = 'cam' + time.strftime("%Y-%m-%d %H.%M.%S") + '.avi'
			write(img, "Recording to %s." % path, window_title=window_title)
			cv2.waitKey(600)
			#cap.record(path)  # Lacks our overlay.
			video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'XVID'), 25, (cap.frame_width, cap.frame_height))
	elif k == 27:  # Esc
		break
	
	frame_count = cap.frame_count
	if (frame_count > old_frame_count) and video:
		old_frame_count = frame_count
		video.write(img)

if video: video.release()
cap.stop()
cv2.destroyAllWindows()