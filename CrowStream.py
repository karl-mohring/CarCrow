import datetime
from SimpleCV import *
import argparse


def get_running_average(image_set):
    """
    Return the average image from an image set
    Useful for calculating a dynamic background
    :param image_set: Set of images to average
    :return: Single image containing the average of the set
    """
    total = Image(image_set[0].size())

    for image in image_set:
        total += image / len(image_set)

    return total


def get_weighted_average(image_set):
    """
    Return the weighted average of an image set
    Averages an image set together, but gives more weight to more recent images
    :param image_set: Image set to average
    :return: Single image containing the weighted average of the set
    """
    if len(image_set):
        weighted_average = reduce('add', [i /float(len(image_set)) for i in image_set])
        return  weighted_average


def append_image_to_set(new_image, image_set, max_frames=30):
    """
    Append an image to an image set.
    Old frames are ejected when the set reaches the max specified size

    :param new_image: New image to be added to the set
    :param image_set: The destination image set
    :param max_frames: The maximum number of frames in the set before old frames are ejected
    :return: Appended image set
    """

    while len(image_set) > max_frames:
        image_set.pop(0)

    image_set.append(new_image)

    return image_set


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
            down = disp.leftButtonDownPosition()

        # End of bounding box
        if disp.leftButtonUp:
            up = disp.leftButtonUpPosition()

        # If the box has been defined, draw it
        if up is not None and down is not None:
            bb = disp.pointsToBoundingBox(up, down)
            image.clearLayers()
            image.drawText(text="Drag again or right click to accept", x=0, y=0, color=Color.HOTPINK, fontsize=20)
            image.drawRectangle(bb[0], bb[1], bb[2], bb[3])
            image.save(disp)

        # Exit if the box is accepted
        if disp.rightButtonDown:
            if bb is not None:
                disp.done = True

    disp.quit()

    return bb


def get_traffic_features(before_image,
                         after_image,
                         threshold=20,
                         erodes=3,
                         dilates=40,
                         smooth_aperture=(19, 19),
                         blob_min=30):
    """
    Find movement features between two video frames.
    Differences between the frames are recognised as movement.
    Optimised for vehicle and pedestrian traffic on my shitty webcam.

    :param before_image: first frame; used as 'background'
    :param after_image: movement frame; movement is detected from this frame
    :param threshold: 'noise floor' for motion detection - pixel value must change by this value for valid movement
    :param erodes: number of erosion iterations. High erosions = only large movements are detected
    :param dilates: number of dilation iterations. Fewer dilations = more separate, smaller movements counted
    :param smooth_aperture: Aperture size for combining movement blobs
    :param blob_min: Cutoff for motion size
    :return: feature set for detected movement
    """

    # Smooth the frames to remove noise, then subtract to find movement
    detect_image = before_image.smooth() - after_image.smooth()

    # Extract features from the differential by processing the crap out of it
    # Everything needs to happen in order: Blur, Threshold, Erode, Dialate, Blur, Blob. BTEDBBl!!
    detect_image = detect_image.threshold(threshold)  # Remove tiny differences in movement
    detect_image = detect_image.erode(iterations=erodes)  # Cut small movements out
    detect_image = detect_image.dilate(
        iterations=dilates)  # Blow up the remaining blobs to combine into large movements
    detect_image = detect_image.smooth(aperature=smooth_aperture)  # Blur blobs together like a lava lamp

    return detect_image.findBlobs(minsize=blob_min)  # Detect and sort out blobs


def draw_bounding_box(image, bounding_box):
    """
    :param bounding_box: Tuple containing x, y, w, h of the bounding box
    :type image: SimpleCV Image object
    """
    image.drawRectangle(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3],
                        color=Color.VIOLET, width=2)


def is_blob_in_detection_area(blob, bounding_box):
    in_detect_area = False
    detect_xmin = bounding_box[0]
    detect_xmax = detect_xmin + bounding_box[2]
    detect_ymin = bounding_box[1]
    detect_ymax = detect_ymin + bounding_box[3]

    # Blob will be detected if the movement covers the bounding box
    if blob.minX() <= detect_xmin and blob.maxX() >= detect_xmax:
        if blob.minY() <= detect_ymin and blob.maxY() >= detect_ymax:
            in_detect_area = True

    # At least 50% of the blob is inside the box
    elif detect_xmin <= blob.centroid()[0] <= detect_xmax:
        if detect_ymin <= blob.centroid()[1] <= detect_ymax:
            in_detect_area = True

    return in_detect_area


def draw_blob(image, blob, colour=Color.RED):
    image.drawRectangle(blob.x - (blob.width() / 2), blob.y - (blob.height() / 2), blob.width(),
                                     blob.height(), color=colour, width=3)
    image.drawCircle(ctr=blob.centroid(), rad=10, color=Color.LEGO_ORANGE, thickness=5)


def draw_features(image, feature_set, bounding_box=None):
    num_detections = 0

    if features is not None:
        for blob in features:
            detection_colour = Color.RED

            if bounding_box is not None and is_blob_in_detection_area(blob, bounding_box):
                    num_detections += 1
                    detection_colour = Color.FORESTGREEN

            draw_blob(next_image, blob, colour=detection_colour)

    return num_detections





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture motion events from a connected webcam')
    parser.add_argument('-d', '--headless', help='Run the program in headless mode', action='store_true')
    parser.add_argument('-X', type=int, help='The x coordinate of the motion detection area')
    parser.add_argument('-Y', type=int, help='The y coordinate of the motion detection area')
    parser.add_argument('-W', '--width', type=int, help='The width of the motion detection area from the start point')
    parser.add_argument('-H', '--height', type=int, help='The height of the motion detection area from the start point')
    parser.add_argument('-i', '--hide-images', help='Do not show the webcam feed (images hidden in headless mode)', action='store_true')
    parser.add_argument('-s', '--no-save', help='Disable saving of motion images', action='store_true')
    parser.add_argument('-l', '--no-log', help='Disable file logging of motion events', action='store_true')
    parser.add_argument('-q', '--quiet', help='Disable logging to console', action='store_true')
    args = parser.parse_args()

    cam = Camera()
    running_average = []

    for x in xrange(0, 30):
        new_image = cam.getImage()
        append_image_to_set(new_image, running_average)

    # Get the detection area from command line if define or running in headless mode
    if args.headless or args.X or args.Y or args.width or args.height:
        detection_area = (args.X, args.Y, args.width, args.height)

    # Grab the detection area visually by default
    else:
        detection_area = get_bounding_box(get_running_average(running_average))

    last_save_timestamp = datetime.datetime.now()

    while True:
        try:
            next_image = cam.getImage()
            draw_bounding_box(next_image, detection_area)
            features = get_traffic_features(get_running_average(running_average), next_image, dilates=60)
            num_detections = draw_features(next_image, features, detection_area)

            # Only count the detection if there are more in the zone compared to last frame
            if num_detections:
                if (datetime.datetime.now() - last_save_timestamp).seconds > 5:
                    last_save_timestamp = datetime.datetime.now()

                    # Save event info if enabled
                    if not args.quiet:
                        print("Motion detected - {}".format(last_save_timestamp.strftime('%Y-%m-%d %H.%M.%S')))

                    if not args.no_save:
                        next_image.save("{}motion {}.jpg".format("", last_save_timestamp.strftime('%Y-%m-%d %H.%M.%S')))

                    if not args.no_log:
                        log_file = open('{} CrowLog.log'.format(last_save_timestamp.strftime('%Y-%m')), mode='a')
                        log_file.write(last_save_timestamp.strftime('%Y-%m-%d %H.%M.%S'))

            if not args.headless and not args.hide_images:
                next_image.show()

            append_image_to_set(next_image, running_average)

        except KeyboardInterrupt:
            sys.exit(0)
