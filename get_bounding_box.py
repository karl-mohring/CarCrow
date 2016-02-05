from time import sleep

from SimpleCV import *


def get_bounding_box(image):
    """
    Get a user-defined bounding box chosen from a given image
    :param image: Input image that is displayed
    :return: list containing x, y, w,h of the bounding box
    """

    disp = Display(resolution=image.size())
    image.drawText(text="Drag a bounding box", x=0, y=0, color=Color.HOTPINK, fontsize=20)
    image.save(disp)

    up = None
    down = None
    bb = None

    while disp.isNotDone():

        # Start of bounding box
        if disp.leftButtonDown:
            up = None
            dwn = disp.leftButtonDownPosition()

        # End of bounding box
        if disp.leftButtonUp:
            up = disp.leftButtonUpPosition()

        # If the box has been defined, draw it
        if up is not None and dwn is not None:
            bb = disp.pointsToBoundingBox(up, dwn)
            image.clearLayers()
            image.drawText(text="Drag again or right click to accept", x=0, y=0, color=Color.HOTPINK, fontsize=20)
            image.drawRectangle(bb[0], bb[1], bb[2], bb[3])
            image.save(disp)

        # Exit if the box is accepted
        if disp.rightButtonDown:
            if bb is not None:
                disp.done = True
    return bb

if __name__ == '__main__':
    image = Image("test.jpg")

    bounding_box = get_bounding_box(image)

    print("Bounding box: {}".format(bounding_box))
