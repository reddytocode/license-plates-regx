from pydarknet import Image
import cv2
from sort import *
import time as time
import DetectPlates
from openalpr import Alpr
from configuraciones import *
from post_process import * 
from videocaptureasync import *
# Return true if line segments AB and CD intersect

alpr = None
COLORS = np.random.randint(0, 255, size=(200, 3), dtype="uint8")
records = {}


#get a list of the posible plates
def rafa(frame):
    car_image = frame[y1:y2, x1:x2, :]
    imgOriginalScene = cv2.resize(car_image, (0, 0), fx=1.4, fy=1.4, interpolation=cv2.INTER_CUBIC)
    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)
    if len(listOfPossiblePlates) > 0:
        points = cv2.boxPoints(listOfPossiblePlates[0].rrLocationOfPlateInScene)

        (xlp1, ylp1) = tuple(points[1])
        (xlp2, ylp2) = tuple(points[2])
        (xlp3, ylp3) = tuple(points[3])
        (xlp0, ylp0) = tuple(points[0])

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
        
        """"said asdf"""
        cv2.line(imgOriginalScene, tuple(points[0]), tuple(points[1]), (0, 255, 0), 2)
        cv2.line(imgOriginalScene, tuple(points[1]), tuple(points[2]), (0, 255, 0), 2)
        cv2.line(imgOriginalScene, tuple(points[2]), tuple(points[3]), (0, 255, 0), 2)
        cv2.line(imgOriginalScene, tuple(points[3]), tuple(points[0]), (0, 255, 0), 2)

        lp_image = imgOriginalScene[int(ylp1):int(ylp3), int(xlp1):int(xlp3), :]
        return True, lp_image
    else:
        return False, None

def process_plates(list_plates):
    dict = {}
    for plate in list_plates:
        if plate in dict:
            dict[plate] = dict[plate] + 1
        else:
            dict[plate] = 1
    #sort by number of appearancess 
    sorted(dict)

def detector_plate(img_plate, alpr, index):
    #print("entro a detector plate")
    try:
        img_str = cv2.imencode('.jpg', img_plate)[1].tostring()
    except:
        img_str = None
    if (not alpr.is_loaded() and img_str == None):
        print("error")
    else:
        #print("alpr loaded")
        results = alpr.recognize_array(img_str)
        for plate in results['results']:           
            for candidate in plate['candidates']:
                type(candidate['plate'])
                prefix = "-"
                if candidate['matches_template']:
                    prefix = "*"
                returned = candidate['plate']
                if (returned != None):
                    print("value of: {} has the plate {}".format(index, returned))
                if(indexIDs[i] in records):
                    records[index].append(returned)
                else:
                    records[index] = []
                """
                for saving the records
                if(indexIDs[i]%10 ==0 and created == False):
                    f= open("records.txt","w+")
                    f.write(str(records))
                    f.close() 
                """
                break

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

if __name__ == '__main__':

    res_reddy = ""
    alpr = alpr_conf()
    tracker = Sort()
    memory = {}
    already_counted = {}
    net = network_conf()
    car_counter = 0
    license_plate = ''
    frame_cycle = 0
    created = False
    debug = True
    #cap = cv2.VideoCapture('/home/docout/Desktop/importante_battleship/Exportación de ACC - 2019-07-09 23.05.46.avi')
    cap = VideoCaptureAsync()
    cap.start()
    while cap.isOpened():
        frame_cycle %= 900
        if frame_cycle == 0:
            already_counted = {}
        grabbed, frame = cap.read()
        if not grabbed:
            break
        line = [(0, 830), (frame.shape[1], 630)]
        (H, W) = frame.shape[:2]
        """debug purposes"""
        if debug:
            cv2.line(frame,(0, 830), (frame.shape[1], 630), (255,10, 30), 1)
            cv2.line(frame,(0, 930), (frame.shape[1], 730), (255,10, 30), 1)
        """--------------"""
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #darknet detection and initialization
        predictions: dict = net.detect(Image(img))
        dets = list()
        for object_class, confidence, (x, y, w, h) in predictions:
            if object_class.decode('utf-8') in ['car', 'bus', 'truck'] and confidence > 0.5:
                x1, y1, x2, y2 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)
                dets.append([x1, y1, x2, y2, confidence])
                if(len(dets) >0):
                    print(type(dets))


        dets = np.asarray(dets)
        tracks = tracker.update(dets)
        """ORIGINAL TRACK"""
        boxes = []
        indexIDs = []
        c = []  #candidates
        previous = memory.copy()
        memory = {}

        for track in tracks:
            boxes.append([track[0], track[1], track[2], track[3]])
            indexIDs.append(int(track[4]))
            memory[indexIDs[-1]] = boxes[-1]
        id_car = 0

        if len(boxes) > 0:
            i = int(0)
            for box in boxes:
                # extract the bounding box coordinates
                (x, y) = (int(box[0]), int(box[1]))
                (w, h) = (int(box[2]), int(box[3]))
                
                """RECTANGLE"""
                color = [int(c) for c in COLORS[indexIDs[i] % len(COLORS)]]
                cv2.rectangle(frame, (x, y), (w, h), color, 2)

                if indexIDs[i] in previous and not indexIDs[i] in already_counted.keys():
                    previous_box = previous[indexIDs[i]]
                    (x2, y2) = (int(previous_box[0]), int(previous_box[1]))
                    (w2, h2) = (int(previous_box[2]), int(previous_box[3]))
                    p0 = (int(x + (w - x) / 2), int(y + (h - y) / 2))
                    p1 = (int(x2 + (w2 - x2) / 2), int(y2 + (h2 - y2) / 2))
                    car_image = frame[y:h, x:w, :]

                    #reddy's try
                    try:
                        #time0 = time.time()
                        detector_plate(car_image, alpr, indexIDs[i])
                        #print("alpr time: ", time.time() - time0)
                    except:
                        print("esto no deberia pasar .. error 185 detector_plate")
                    #time0 = time.time()    
                    bool_value = intersect(p0, p1, line[0], line[1])
                    #print(time.time() - time0)
                    if bool_value:
                        cv2.line(frame,(0, 830), (frame.shape[1], 630), (0, 0, 255), 1)
                        #print(records[indexIDs[i]])
                        try:
                            res_reddy = choose_the_best(records[indexIDs[i]])
                            if(res_reddy == None):
                                print("[INFO] es posible que la placa sea una antiua")
                                res_reddy = find_old_plate(records[indexIDs[i]])
                            print("**************************")
                            print(res_reddy)
                            print("**************************")
                        except:
                            print("**************************")
                            print("failed")
                            print("**************************")
                            res_reddy = "None"
                            
                        # print(indexIDs)
                        # print(memory)
                        # print(already_counted)
                        already_counted[indexIDs[i]] = True
                        car_counter += 1

                        x1, y1, x2, y2 = x, y, w, h
                        """Licence Plate Detection"""
                        """
                        return: 
                            - results
                        takes:
                            - frame

                        created:

                            - car_image
                            - imgOriginalScene
                            - listOfPossiblePlates
                            - points
                        """                       
                        rafa_condition, auxReddy = rafa(frame)
                        if(rafa_condition):
                            print("rafa is not None")

                            results = alpr.recognize_ndarray(auxReddy)
                            i = 0
                            for plate in results['results']:
                                candidates = sorted(plate['candidates'], key=lambda c: (len(c['plate']), c['confidence']), reverse=True)
                                candidate = candidates[0]
                                license_plate = candidate['plate']
                                id_car = indexIDs[i]
                                for c in candidates:
                                    print(c['confidence'], c['matches_template'], c['plate'], sep='; ')

                text = "{}".format(indexIDs[i])
                cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                i += 1

        # draw car_counter
        cv2.putText(frame, str(car_counter), (100, 200), cv2.FONT_HERSHEY_DUPLEX, 5.0, (0, 255, 255), 10)
        cv2.putText(frame, str(id_car)  + " : "+license_plate.upper(), (300, 200), cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 255, 255), 4)
        cv2.putText(frame, str(id_car)  + " : "+str(res_reddy), (300, 300), cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 255, 255), 4)

        
        cv2.imshow('Frame', frame)
        frame_cycle += 1

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.stop()