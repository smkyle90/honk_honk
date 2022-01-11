import cv2
import json


class Imager:
    def __init__(self):
        # define a video capture object
        self.vid = cv2.VideoCapture(0)
  
        self.__ret = False
        self.__frame = None

    def read(self):
        if self.vid.isOpened():
            self.__ret, self.__frame = self.vid.read()
        else:
            self.__ret = False

    def as_json(self):
        if self.__ret:
            img_as_list = self.__frame.tolist()
        else:
            img_as_list = []

        return json.dumps(img_as_list)

    def close(self):
        # After the loop release the cap object
        self.vid.release()

        # Destroy all the windows
        cv2.destroyAllWindows()
