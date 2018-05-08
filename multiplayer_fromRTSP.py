"""
video streaming application
[Tokyo SDK Development - Task #3640] Implement an in-house player for video bitstream
•   Assignee: Takchoi.Yu im147

•   Target version: 
the in-house player should be able to receive bitstream from RTSP server.
In addition, the player can decoded the metadata and do the correct thing, including: 
•   Get the object list in the current frame, and draw the object bounding boxes to the video.

Functional Spec:
1.  The player is executed from command line, a URL is passed to the player.
2.  
3.  > multiplayer -u <URL>
4.  A window pops up, displaying the video stream. 
o   When the window is not maximized, the psdndow frame or press Ctrl-C from command line, the program terminates.

"""
import cv2
import argparse
import sys
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-u","--url", help="input rtsp streaming url")
args = parser.parse_args()

class Bbox(object):
    """
    bbox - bounding box information
    properties:
        _x1,_y1 - top left coordinate
        _x2,_y2 - bottom right coordinate
        speed - not implemented yet
    """
    def __init__(self,bbox=None,if_random=False,image_dim = None):
        if bbox is not None:
            self._x1, self._y1, self._x2, self._y2 = bbox
        else:
            if if_random:
                h, w = image_dim
                self._x1, self._y1 = np.int(np.random.rand()*w*0.2), np.int(np.random.rand()*h*0.2)
                self._x2, self._y2 = np.int(self._x1+w*0.3), np.int(self._y1+h*0.2)

    def get_bbox(self):
        return  self._x1, self._y1, self._x2, self._y2
    def get_speed(self):
        pass


class Bbox_list(object):
    """
    list of bbox
    Properties:
        bbox_list - list of bbox
        add_bbox()
        get_bbox()
        create_bbox()
    """

    def __init__(self):
        self.bbox_list = []
        self.len = 0

    def add_bbox(self,bbox):
        self.bbox_list.append(bbox)

    def get_bbox_from_list(self):
        for bbox in self.bbox_list:
            yield(bbox)

    def create_bbox(self, num , image_dim):

        for num_ in range(num+1):
            self.bbox_list.append(Bbox(bbox = None,if_random = 1,image_dim = image_dim))
            self.len = self.len+1
   
class multiplayer(object):

    GREEN = (0,255,0)

    def __init__(self,rtsp=None):
        if rtsp is None:
            sys.exit("Exception: no input args")    

        self.rtsp = rtsp
        self.vcap = cv2.VideoCapture(rtsp)        
        self.if_detect = 1 
        self.if_create_bbox = 1

        if not self.vcap.isOpened():
            print("cannot open", rtsp)
            if self.rtsp.find('rtsp')>-1:
                print("Please make sure username and password are provided in the rtsp url\n")
            sys.exit("exit -1: invalid url")
    
    def _read(self):

        _, self.fr = self.vcap.read()

        if self.if_detect:
            if not self.if_create_bbox:
                bbox_list = self._detection()
            else:               
                self.image_dim = self.fr.shape[0:2]
                bbox_list = Bbox_list()
                bbox_list.create_bbox(1,self.image_dim)

            self._insert_bbox_list(bbox_list)            
    
    def _show(self):

        cv2.namedWindow("video", cv2.WINDOW_NORMAL )
        cv2.imshow("video", self.fr)
        
    def _insert_bbox_list(self, bbox_list):

        for bbox in bbox_list.get_bbox_from_list():
            x1,y1,x2,y2 = bbox.get_bbox()
            cv2.rectangle(self.fr,(x1,y1),(x2,y2), self.GREEN ,3)
    
    def _detection(self):

        pass

    def play(self):

        print('Press key ''q'' to quit application: ...\n')
        while(1):
            self._read() 
            self._show()            

            c = cv2.waitKey(30)
            if c == ord('q') :
                self.vcap.release()
                cv2.destroyAllWindows()
                sys.exit("exit 0 - close successfully")
        
if __name__ == "__main__":
    #args.url = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
    #args.url = "rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov"
    #args.url = "rtsp://127.0.0.1:8554/stream"
    args.url = "rtsp://admin:multitek123@192.168.10.107:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1"
    player  = multiplayer(args.url)
    player.play()
    
    
    
