from CarCrow import *
from SimpleCV import *


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

    cam = Camera()
    image = cam.getImage()
    detection_area = get_bounding_box(image)

    last_save_timestamp = datetime.datetime.now()

    while True:
        next_image = cam.getImage()
        draw_bounding_box(next_image, detection_area)
        features = get_traffic_features(image, next_image, dilates=60)
        num_detections = draw_features(next_image, features, detection_area)

        # Only count the detection if there are more in the zone compared to last frame
        if num_detections:
            if (datetime.datetime.now() - last_save_timestamp).seconds > 5:
                last_save_timestamp = datetime.datetime.now()
                next_image.save("{}motion {}.jpg".format("", datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')))

        next_image.show()

        image = next_image

def main(argv):
