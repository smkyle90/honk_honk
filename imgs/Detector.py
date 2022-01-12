from ctypes import *
import random
import os
import cv2
import time
import darknet
import argparse
from threading import Thread, enumerate
from queue import Queue
import json
from .Subber import Subber
import numpy as np


class Detector(Subber):
    def __init__(self, addr, port, save_categories=None, show_video=False, use_zmq=False):
        super().__init__(addr, port)
        
        self.use_zmq = use_zmq
        self.cap = cv2.VideoCapture("http://{}:8081".format(addr))

        self.show_video = show_video

        self.frame_queue = Queue()
        self.darknet_image_queue = Queue(maxsize=1)
        self.detections_queue = Queue(maxsize=1)
        self.fps_queue = Queue(maxsize=1)
        
        self.args = self.parser()
        self.check_arguments_errors()

        self.network, self.class_names, self.class_colors = darknet.load_network(
            self.args.config_file,
            self.args.data_file,
            self.args.weights,
            batch_size=1
        )

        self.width = darknet.network_width(self.network)
        self.height = darknet.network_height(self.network)

        self.save_categories = save_categories
        self.__save_img = False

    def spin(self):
        t1 = Thread(target=self.get_frame, args=())
        t2 = Thread(target=self.inference, args=())
        t3 = Thread(target=self.output, args=())

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

    def parser(self):
        parser = argparse.ArgumentParser(description="YOLO Object Detection")
        parser.add_argument("--input", type=str, default=0,
                            help="video source. If empty, uses webcam 0 stream")
        parser.add_argument("--out_filename", type=str, default="",
                            help="inference video name. Not saved if empty")
        parser.add_argument("--weights", default="yolov4.weights",
                            help="yolo weights path")
        # parser.add_argument("--dont_show", action='store_true',
        #                     help="windown inference display. For headless systems")
        parser.add_argument("--ext_output", action='store_true',
                            help="display bbox coordinates of detected objects")
        parser.add_argument("--config_file", default="./cfg/yolov4.cfg",
                            help="path to config file")
        parser.add_argument("--data_file", default="./cfg/coco.data",
                            help="path to data file")
        parser.add_argument("--thresh", type=float, default=0.5,
                            help="remove detections with confidence below this value")
        return parser.parse_args()


    def check_arguments_errors(self):
        assert 0 < self.args.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
        if not os.path.exists(self.args.config_file):
            raise(ValueError("Invalid config path {}".format(os.path.abspath(self.args.config_file))))
        if not os.path.exists(self.args.weights):
            raise(ValueError("Invalid weight path {}".format(os.path.abspath(self.args.weights))))
        if not os.path.exists(self.args.data_file):
            raise(ValueError("Invalid data file path {}".format(os.path.abspath(self.args.data_file))))


    def set_saved_video(self, input_video, output_video, size):
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        fps = int(input_video.get(cv2.CAP_PROP_FPS))
        video = cv2.VideoWriter(output_video, fourcc, fps, size)
        return video


    def get_frame(self):
        while True:
            if self.use_zmq:
                img_json = self.sub()
                img_data = json.loads(img_json)
                img_arr = np.asarray(img_data).astype(np.uint8)
            elif self.cap.isOpened():
                ret, img_arr = self.cap.read()
            else:
                raise RuntimeError("Need to get frames from zmq or http.") 

            frame_rgb = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
            
            frame_resized = cv2.resize(frame_rgb, (self.width, self.height),
                                       interpolation=cv2.INTER_LINEAR)
            
            self.frame_queue.put(frame_resized)
            img_for_detect = darknet.make_image(self.width, self.height, 3)
            darknet.copy_image_from_bytes(img_for_detect, frame_resized.tobytes())
            self.darknet_image_queue.put(img_for_detect)

    def inference(self):
        while True:
            darknet_image = self.darknet_image_queue.get()
            prev_time = time.time()
            detections = darknet.detect_image(self.network, self.class_names, darknet_image, thresh=self.args.thresh)
            self.detections_queue.put(detections)
            fps = int(1/(time.time() - prev_time))
            self.fps_queue.put(fps)
            print("FPS: {}".format(fps))

            self.check_detections(detections, darknet_image)

            darknet.print_detections(detections, self.args.ext_output)
            darknet.free_image(darknet_image)
        
    def check_detections(self, detections, img):

        self.__save_img = False

        if self.save_categories is None:
            pass
        elif self.save_categories:
            det_type = set([det[0] for det in detections])
            save_cats = set(self.save_categories)
            
            self.__save_img = bool(det_type.intersection(save_cats))

    def output(self, output_dir="./out"):
        random.seed(3)  # deterministic bbox colors

        while True:
            frame_resized = self.frame_queue.get()
            detections = self.detections_queue.get()
            fps = self.fps_queue.get()

            if frame_resized is not None:
                image = darknet.draw_boxes(detections, frame_resized, self.class_colors)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


                if self.show_video:
                    cv2.imshow('Inference', image)
                elif self.__save_img:
                    cv2.imwrite(f"{output_dir}/{int(time.time())}.jpeg", image)

                if cv2.waitKey(fps) == 27:
                    break
