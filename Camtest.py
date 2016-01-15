__author__ = 'Leenix'

from SimpleCV import *

cam = Camera(0)

while True:
    frame = cam.getImage()
    frame.show()
    time.sleep(0.2)

