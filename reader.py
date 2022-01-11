
from imgs import Subber
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import cv2
addr = "192.168.0.207"
port = "5556"

s = Subber(addr, port)
fig = plt.figure()
ax = fig.add_subplot(111)

# pre trained Car and Pedestrian classifiers
car_classifier = './xmls/cars.xml'

# create trackers using classifiers using OpenCV
car_tracker = cv2.CascadeClassifier(car_classifier)

plt.ion()
while True:
    ax.clear()
    img_json = s.sub()
    img_data = json.loads(img_json)
    img_arr = np.asarray(img_data).astype(np.uint8)

    # convert color image to grey image
    gray_img = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY)

    # detect cars
    cars = car_tracker.detectMultiScale(gray_img)

    # draw rectangle around the cars
    for (x,y,w,h) in cars:
        cv2.rectangle(img_arr, (x,y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(img_arr, 'Car', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    try:
        if cars.tolist():
            cv2.imwrite(f"./img/{int(time.time())}.jpeg", img_arr)
    except Exception:
        pass

    # ax.imshow(img_arr)
    # plt.show()
    # plt.pause(0.001)

