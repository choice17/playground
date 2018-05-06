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

parser = argparse.ArgumentParser()
parser.add_argument("-u","--url", help="input rstp streaming url")
args = parser.parse_args()

    
class multiplayer(object):
    
    def __init__(self,rstp=None):
        if rstp is None:
            sys.exit("Exception: no input args")
                    
        self.rstp = rstp
        self.vcap = cv2.VideoCapture(rstp)  
        if not self.vcap.isOpened():
            print("cannot open ", rstp)
            sys.exit()
    
    def _read(self):
        self.ret, self.fr = self.vcap.read()
    
    def _show(self):
        cv2.namedWindow("video", cv2.WINDOW_NORMAL )
        cv2.imshow("video", self.fr)
        
    def play(self):
    
        while(1):
            self._read()
            self._show()
            c = cv2.waitKey(30)
            if c == ord('q') :
                self.vcap.release()
                cv2.destroyAllWindows()
                break
        
if __name__ == "__main__":
    #args.url = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
    args.url = "rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov"
    #args.url = "rtsp://127.0.0.1:8554/stream"
    #args.url = "http://192.168.0.3:8080/stream"
    player  = multiplayer(args.url)
    player.play()
    
    
        
    