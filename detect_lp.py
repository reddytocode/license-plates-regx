import cv2
import numpy as np
from pydarknet import Detector, Image

from openalpr import Alpr

import DetectPlates

cap = cv2.VideoCapture('/home/nubol23/Videos/Exportación de ACC - 2019-07-09 23.05.46.avi')

net = Detector(bytes("/home/nubol23/Desktop/Codes/DOCOUT/alpr-unconstrained/data/vehicle-detector/yolo-voc.cfg", encoding="utf-8"),
               bytes("/home/nubol23/Desktop/Codes/DOCOUT/alpr-unconstrained/data/vehicle-detector/yolo-voc.weights", encoding="utf-8"),
               0,
               bytes("/home/nubol23/Desktop/Codes/DOCOUT/alpr-unconstrained/data/vehicle-detector/voc.data", encoding="utf-8"))

alpr = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
alpr.set_top_n(7)
alpr.set_default_region("wa")
alpr.set_detect_region(False)

while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret:

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        predictions: dict = net.detect(Image(rgb_frame))

        # cars = []
        for object_class, confidence, (x, y, w, h) in predictions:
            if object_class.decode('utf-8') in ['car', 'bus', 'truck']:
                x1, y1, x2, y2 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)
                # cars.append(rgb_frame[y1:y2, x1:x2])
                # car_image = rgb_frame[y1+(y2//2):y2, x1+(x2//2):x2]
                car_image = rgb_frame[y1:y2, x1:x2, :]
                # car_image = cv2.resize(car_image, (1024, 640))
                # car_image = cv2.resize(car_image, (1024, 640))

                imgOriginalScene = cv2.resize(car_image, (0, 0), fx=1.4, fy=1.4, interpolation=cv2.INTER_CUBIC)
                listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)
                if len(listOfPossiblePlates) > 0:
                    points = cv2.boxPoints(listOfPossiblePlates[0].rrLocationOfPlateInScene)

                    (x1, y1) = tuple(points[1])
                    (x2, y2) = tuple(points[2])
                    (x3, y3) = tuple(points[3])
                    (x0, y0) = tuple(points[0])

                    hb = 10
                    vb = 15

                    points[1] = (x1 - hb, y1 - vb)
                    points[2] = (x2 + hb, y2 - vb)
                    points[3] = (x3 + hb, y3 + vb)
                    points[0] = (x0 - hb, y0 + vb)

                    (x1, y1) = tuple(points[1])
                    (x2, y2) = tuple(points[2])
                    (x3, y3) = tuple(points[3])
                    (x0, y0) = tuple(points[0])

                    x1 = max(0, x1)
                    x0 = max(0, x0)
                    x2 = min(x2, frame.shape[1])
                    x3 = min(x3, frame.shape[1])

                    y1 = max(0, y1)
                    y2 = max(0, y2)
                    y0 = min(y0, frame.shape[1])
                    y3 = min(y3, frame.shape[1])

                    cv2.line(imgOriginalScene, tuple(points[0]), tuple(points[1]), (0, 255, 0), 2)
                    cv2.line(imgOriginalScene, tuple(points[1]), tuple(points[2]), (0, 255, 0), 2)
                    cv2.line(imgOriginalScene, tuple(points[2]), tuple(points[3]), (0, 255, 0), 2)
                    cv2.line(imgOriginalScene, tuple(points[3]), tuple(points[0]), (0, 255, 0), 2)

                    cv2.imshow('LP', imgOriginalScene)

                    lp_image = imgOriginalScene[int(y1):int(y3), int(x1):int(x3), :]
                    cv2.imshow('LP_IMG', lp_image)

                    """--------------------------------"""
                    results = alpr.recognize_ndarray(lp_image)
                    i = 0
                    for plate in results['results']:
                        candidate = sorted(plate['candidates'], key=lambda c: c['confidence'], reverse=True)[0]
                        #     print(candidate['confidence'], candidate['matches_template'], candidate['plate'])
                        print('PLATE:', candidate['plate'])
                    """--------------------------------"""

                # results = alpr.recognize_ndarray(car_image)
                #
                # i = 0
                # for plate in results['results']:
                #     i += 1
                #     # print("Plate #%d" % i)
                #     # print("   %12s %12s" % ("Plate", "Confidence"))
                #     for candidate in plate['candidates']:
                #         # prefix = "-"
                #         if candidate['matches_template']:
                #             # print(type(candidate['confidence']), candidate['confidence'] > 80.0)
                #             if candidate['confidence'] > 80.0:
                #                 print(candidate['plate'])
                #             # prefix = "*"
                #
                #         # print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))
                #
                # # cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imshow('Frame', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    else:
        break

cap.release()

cv2.destroyAllWindows()
