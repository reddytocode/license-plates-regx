import DetectPlates
import cv2

frame = cv2.imread("a.png")
listOfPossiblePlates = DetectPlates.detectPlatesInScene(frame)

if len(listOfPossiblePlates) > 0:
    points = cv2.boxPoints(listOfPossiblePlates[0].rrLocationOfPlateInScene)

    (xlp1, ylp1) = tuple(points[1])
    (xlp2, ylp2) = tuple(points[2])
    (xlp3, ylp3) = tuple(points[3])
    (xlp0, ylp0) = tuple(points[0])
    cv2.circle(frame, (xlp1, ylp1), 3, (0, 0, 255))
    cv2.circle(frame, (xlp2, ylp2), 3, (0, 0, 255))
    cv2.circle(frame, (xlp3, ylp3), 3, (0, 0, 255))
    cv2.circle(frame, (xlp0, ylp0), 3, (0, 0, 255))

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

    lp_image = frame[int(ylp1):int(ylp3), int(xlp1):int(xlp3), :]
    cv2.imwrite("lp_image.jpg", lp_image)
cv2.imwrite("frame.jpg", frame)