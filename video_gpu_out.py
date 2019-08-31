from pydarknet import Detector, Image
import cv2
from sort import *
import time as t

import DetectPlates

from openalpr import Alpr


# Return true if line segments AB and CD intersect
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


if __name__ == '__main__':
    alpr = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
    alpr.set_top_n(7)
    alpr.set_default_region("wa")
    alpr.set_detect_region(False)

    tracker = Sort()
    memory = {}
    already_counted = {}

    net = Detector(bytes("data/vehicle-detector/yolo-voc.cfg", encoding="utf-8"),
                   bytes("data/vehicle-detector/yolo-voc.weights", encoding="utf-8"),
                   0,
                   bytes("data/vehicle-detector/voc.data", encoding="utf-8"))

    counter = 0
    license_plate = ''

    COLORS = np.random.randint(0, 255, size=(200, 3), dtype="uint8")

    cap = cv2.VideoCapture('/home/nubol23/Videos/Exportación de ACC - 2019-07-09 23.05.46.avi')

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('counter_lp.mp4', cv2.VideoWriter_fourcc(*'MP4V'), 120, (frame_width, frame_height))

    # cap = cv2.VideoCapture('/home/docout/Desktop/Exportación de ACC - 2019-07-09 23.05.46.avi')
    frame_cycle = 0
    while cap.isOpened():
        frame_cycle %= 900
        # print(frame_cycle)
        if frame_cycle == 0:
            already_counted = {}

        # read the next frame from the file
        (grabbed, frame) = cap.read()
        # line = [(500, 500), (1200, 400)]
        # line = [(0, 800), (frame.shape[1], 600)]

        # line = [(0, 700), (frame.shape[1], 500)]
        line = [(0, 630), (frame.shape[1], 430)]

        # if the frame was not grabbed, then we have reached the end
        # of the stream
        if not grabbed:
            break

        """create backup of frame"""
        frame_bak = frame.copy()
        bak_h, bak_w = frame_bak.shape[:2]

        """resize frame to half original size"""
        frame = cv2.resize(frame, (bak_w // 2, bak_h // 2))

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        """predict on smaller frame"""
        predictions: dict = net.detect(Image(img))

        """restore original size frame"""
        frame = frame_bak
        (H, W) = frame.shape[:2]

        dets = list()
        for object_class, confidence, (x, y, w, h) in predictions:
            if object_class.decode('utf-8') in ['car', 'bus', 'truck'] and confidence > 0.5:
                x1, y1, x2, y2 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)

                """
                duplicate pixel size from predictions because they were inferred over
                smaller frame, and convert value to integer
                """
                x1, y1, x2, y2 = int(x1 * 2), int(y1 * 2), int(x2 * 2), int(y2 * 2)

                dets.append([x1, y1, x2, y2, confidence])

        np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
        dets = np.asarray(dets)
        # print('DETS:', dets)
        tracks = tracker.update(dets)

        """ORIGINAL TRACK"""
        boxes = []
        indexIDs = []
        c = []
        previous = memory.copy()
        memory = {}

        for track in tracks:
            boxes.append([track[0], track[1], track[2], track[3]])
            indexIDs.append(int(track[4]))
            memory[indexIDs[-1]] = boxes[-1]

        if len(boxes) > 0:
            i = int(0)
            for box in boxes:
                # extract the bounding box coordinates
                (x, y) = (int(box[0]), int(box[1]))
                (w, h) = (int(box[2]), int(box[3]))

                # draw a bounding box rectangle and label on the image
                # color = [int(c) for c in COLORS[classIDs[i]]]
                # cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

                """RECTANGLE"""
                # color = [int(c) for c in COLORS[indexIDs[i] % len(COLORS)]]
                # cv2.rectangle(frame, (x, y), (w, h), color, 2)

                if indexIDs[i] in previous and not indexIDs[i] in already_counted.keys():
                    previous_box = previous[indexIDs[i]]
                    (x2, y2) = (int(previous_box[0]), int(previous_box[1]))
                    (w2, h2) = (int(previous_box[2]), int(previous_box[3]))
                    p0 = (int(x + (w - x) / 2), int(y + (h - y) / 2))
                    p1 = (int(x2 + (w2 - x2) / 2), int(y2 + (h2 - y2) / 2))
                    """LINE"""
                    # cv2.line(frame, p0, p1, color, 3)

                    if intersect(p0, p1, line[0], line[1]):
                        # print(indexIDs)
                        # print(memory)
                        # print(already_counted)
                        already_counted[indexIDs[i]] = True
                        counter += 1

                        x1, y1, x2, y2 = x, y, w, h
                        """Licence Plate Detection"""
                        car_image = frame[y1:y2, x1:x2, :]

                        # cv2.imwrite('cars/car_'+str(indexIDs[i])+'.png', car_image)

                        imgOriginalScene = cv2.resize(car_image, (0, 0), fx=1.4, fy=1.4, interpolation=cv2.INTER_CUBIC)
                        # listOfPossiblePlates = DetectPlates.detectPlatesInScene(car_image)
                        listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)
                        if len(listOfPossiblePlates) > 0:
                            points = cv2.boxPoints(listOfPossiblePlates[0].rrLocationOfPlateInScene)

                            (xlp1, ylp1) = tuple(points[1])
                            (xlp2, ylp2) = tuple(points[2])
                            (xlp3, ylp3) = tuple(points[3])
                            (xlp0, ylp0) = tuple(points[0])

                            # hb = 10
                            # vb = 15
                            hb = 20
                            vb = 20

                            points[1] = (xlp1 - hb, ylp1 - vb)
                            points[2] = (xlp2 + hb, ylp2 - vb)
                            points[3] = (xlp3 + hb, ylp3 + vb)
                            points[0] = (xlp0 - hb, ylp0 + vb)

                            (xlp1, ylp1) = tuple(points[1])
                            (xlp2, ylp2) = tuple(points[2])
                            (xlp3, ylp3) = tuple(points[3])
                            (xlp0, ylp0) = tuple(points[0])

                            xlp1 = max(0, xlp1)
                            xlp0 = max(0, xlp0)
                            xlp2 = min(xlp2, frame.shape[1])
                            xlp3 = min(xlp3, frame.shape[1])

                            ylp1 = max(0, ylp1)
                            ylp2 = max(0, ylp2)
                            ylp0 = min(ylp0, frame.shape[1])
                            ylp3 = min(ylp3, frame.shape[1])

                            # cv2.line(imgOriginalScene, tuple(points[0]), tuple(points[1]), (0, 255, 0), 2)
                            # cv2.line(imgOriginalScene, tuple(points[1]), tuple(points[2]), (0, 255, 0), 2)
                            # cv2.line(imgOriginalScene, tuple(points[2]), tuple(points[3]), (0, 255, 0), 2)
                            # cv2.line(imgOriginalScene, tuple(points[3]), tuple(points[0]), (0, 255, 0), 2)

                            # cv2.imshow('LP', imgOriginalScene)

                            lp_image = imgOriginalScene[int(ylp1):int(ylp3), int(xlp1):int(xlp3), :]
                            # cv2.imwrite('cars/car_' + str(indexIDs[i]) + '_lp.png', lp_image)
                            # cv2.imshow('LP_IMG', lp_image)

                            """--------------------------------"""
                            results = alpr.recognize_ndarray(lp_image)
                            i = 0
                            for plate in results['results']:
                                candidates = sorted(plate['candidates'], key=lambda c: c['confidence'], reverse=True)
                                candidate = candidates[0]
                                #     print(candidate['confidence'], candidate['matches_template'], candidate['plate'])
                                license_plate = candidate['plate']
                                # for c in candidates:
                                #     print(c['confidence'], c['matches_template'], c['plate'], sep='; ')
                            """--------------------------------"""
                        """-----------------------"""

                """ID"""
                # text = "{}".format(indexIDs[i])
                # cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                i += 1

        """LINE"""
        # cv2.line(frame, line[0], line[1], (0, 255, 255), 5)

        # draw counter
        cv2.putText(frame, str(counter), (100, 200), cv2.FONT_HERSHEY_DUPLEX, 5.0, (0, 255, 255), 10)
        cv2.putText(frame, license_plate, (300, 200), cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 255, 255), 4)
        # counter += 1

        # saves image file
        # cv2.imwrite("output/frame-{}.png".format(frameIndex), frame)
        cv2.imshow('Frame', frame)
        out.write(cv2.resize(frame, (frame.shape[1], frame.shape[0])))
        frame_cycle += 1

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()
    out.release()
