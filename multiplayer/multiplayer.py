
#import random
#import time

import threading            
import queue
import subprocess as sp
import cv2
import sys
import argparse
import time 
import binascii as bi
import xml.etree.ElementTree as ET


parser = argparse.ArgumentParser()
parser.add_argument("-u","--url", help="input streaming url")
parser.add_argument("-v","--verbose", help="input streaming url")
args = parser.parse_args()

class Bbox(object):
    """
    objective: bbox - stores a bounding box information
    properties:
        _sx,_sy - top left coordinate
        _ex,_ey - bottom right coordinate
        speed - not implemented yet
    """
    def __init__(self,bbox=None,if_random=False,image_dim = None):
        if bbox is not None:
            self._sx, self._sy, self._ex, self._ey = bbox
        else:
            if if_random:
                if image_dim is None:
                    return None
                h, w = image_dim
                self._sx, self._sy = np.int(np.random.rand()*w*0.2), np.int(np.random.rand()*h*0.2)
                self._ex, self._ey = np.int(self._sx+w*0.3), np.int(self._sy+h*0.2)

    
    def get(self):
        return  self._sx, self._sy, self._ex, self._ey
    def get_speed(self):
        pass


class Bbox_list(list):
    """
    objective: list of bbox
    Properties:
        bbox_list - list of bbox
        add_bbox()
        get_bbox()
        create_bbox()
    """

    def __init__(self,bbox=None):
        super(Bbox_list,self).__init__()        
        #super().__init__()
        self.len = 0
        if bbox is not None:
            self.append(bbox)

    def append(self,bbox):
        if type(bbox) != 'list':
            super(Bbox_list,self).append(bbox)
            self.len = self.len + 1       

    def get_bbox_from_list(self):
        for bbox in self:
            yield(bbox.get())

    def create_bbox(self, num , image_dim):
        for num_ in range(num+1):
            self.append(Bbox(bbox = None,if_random = 1,image_dim = image_dim))
            self.len = self.len+1


class RUN:
    

    def __init__(self,opts):        

        """
        RUN class is to store function running as thread
        main function:
            1. cv_fn : get image from stream
            2. srt_fn : broadcast video stream and pipe outout
        variables:
            localudp            : broadcast at udp addr
            isStart             : determine if the stream is started (for refresh)
            fontFormat          : font format for drawing function cv2.putText()
            imageSize           : allow draw function to adapt to the image size
            verbose             : for subtitle display 0: no | 1: terminal and text | 2: terminal only | 3: terminal and bbox
            COLOR               : color constant
            is_cvIdle           : for video idle handle
            cvIdle_start_time   : for video idle handle
        """    
        self.name = 'multiplayer'
        self.localudp = 'udp://127.0.0.1:12345'
        self.isCVStart = True
        self.isSRTStart = True
        self.COLOR = {
            'GREEN':(0,255,0),
            'BLACK':(0,0,0),
            'WHILE':(255,255,255),
            'RED':(255,0,0),
            'BLUE':(0,0,255)
        }  
        self.fontFormat = {
            'font':cv2.FONT_HERSHEY_SIMPLEX,
            'bottomLeftCornerOfText':(10,500),
            'fontScale':0.5,
            'fontColor':self.COLOR['WHILE'],
            'thickness':1,
            'lineType':cv2.LINE_AA 
        }
        self.imageSize = {}
        self.verbose = 3 # display msg in frame and shell
        self.is_cvIdle = False
        self.cvIdle_start_time = 0

        for 
    
    def cv_fn(self,url,q):
        """
        objective: 
            read frame and put image in the queue
        var:
            url : local udp broadcast from srt_fn()
            q   : queue.Queue() instance
        """

        self.cap = cv2.VideoCapture(self.localudp)        
        
        if not self.cap.isOpened():            
            sys.exit('exit -1 cannot open %s' % self.localudp)
        
        _,fr = self.cap.read()
        h,w,c = fr.shape
        self.imageSize = {'h':h,'w':w,'c':c}
        try:
            cv2.resizeWindow(self.url,self.imageSize['h'],self.imageSize['w'])
        except:
            pass
        self.fontFormat['bottomLeftCornerOfText'] = (10,h-10)#(int(h/10),int(w/4))
        self.fontFormat['fontScale'] = (0.5 + 0.5*h/1280)*(1 + 2*h/1280)
        self.fontFormat['thickness'] = int((0.5 + 0.5*h/1280)*(1 + 3*h/1280))

        while True:
            boo,fr = self.cap.read()
            #print('can read r')
            if boo:
                q.put(['image',fr])  

    def srt_fn(self,url,q):
        """
        main function to call in threading
        objective: 
            1. srt_fn() broadcast rtsp to local udp to read video  X
            2. srt_fun() pipe srt                                  X  
            3. parse() parse raw binary                            O to be changed according to different format
            4. parse() connect string between frames               X
            5. decode_xml() decode string to xml                   O to be change according to different format
            6. get_bbox_from_xml() decode xml to bbox list         X 
        variable:
            url : streaming url
            q   : queue.Queue() instance           

        """
        xmlKey = '3c6f6c3e' # '<ol>'
        subKey = "->" 
        cmd = 'ffmpeg -v fatal -i %s -an -f mpegts %s -vn -f srt -' % (url,self.localudp)
        msg_parser = {'idx':0 ,'content':'','msg':''}       
        subTimeConnect = 0.01 # 10ms
        neglectStrLen = 10 #

        def get_bbox_from_xml(decodexml):
            root = ET.fromstring(decodexml)
            obj_num = 0
            box_list = Bbox_list()
            for coords in root.findall('object'):
                box_list.append(Bbox(bbox=[int(coord.text) for coord in coords[:4]]))                
                #print(root[0].tag,root[0].text, [ (j.tag,int(j.text)) for j in coords[:4] ] )
            
            return box_list

        def decode_xml(raw_msg):            
            if raw_msg[:8] == xmlKey:
                try:                
                    raw_msg = bytes ( raw_msg,'utf-8')                    
                    decode_msg = bi.unhexlify(raw_msg).decode()
                    # comment for debug
                    decode_msg = get_bbox_from_xml(decode_msg)
                    #print('0\n',decode_msg)
                    return decode_msg
                except bi.Error as e:
                    print(e)
                    if e == 'binascii.Error: Odd-length string':
                        raw_msg = bytes (raw_msg[:-1],'utf-8')                    
                        decode_msg = bi.unhexlify(raw_msg).decode()
                        # comment for debug
                        decode_msg = get_bbox_from_xml(decode_msg)
                        return decode_msg
                    #print(raw_msg)
                    return raw_msg
            else: 
                return raw_msg

        def parse(raw_msg,time_duration):

            """
            objective: parsing raw message, built in to srt_fn()
            variable:
                msg_parser : parser
                raw_msg    : output from pipe 
                time_duration : to define if the raw msg is connected

            logic here:
                1.  if find srt key '->'
                        if srt start streaming
                            do false on start streaming
                        else do decode srt
                        do refresh msg_parser
                    else if msg_parser is refreshed
                        if coming srt is shorter than defined connected time time_duration
                            if msg_parser content is '' empty
                                do get raw_msg
                            else if raw_msg is long enough
                                do concat msg_parser content
                        else do decode srt
                            if verbose flag is on
                                do print msg_parser output msg
                            do refresh msg_parser

            """
            if raw_msg.find(subKey)>-1:                        
                if self.isSRTStart:
                    self.isSRTStart = False
                else:
                    if self.verbose == 3:
                        msg_parser['msg'] = decode_xml(msg_parser['content'])
                    else:
                        msg_parser['msg'] = msg_parser['content']
                msg_parser['idx'] = 1
                msg_parser['content'] = ''

            elif msg_parser['idx'] == 1:                     
                    if  time_duration < subTimeConnect:
                        if msg_parser['content'] == '':
                            msg_parser['content'] = raw_msg
                        else:
                            if len(raw_msg)>neglectStrLen:
                                msg_parser['content'] = msg_parser['content'] + raw_msg                                
                    else:
                        if self.verbose == 3:
                            msg_parser['msg'] = decode_xml(msg_parser['content'])
                        else:
                            msg_parser['msg'] = msg_parser['content']
                        
                        if self.verbose!=0:                            
                            try:
                                print([box for box in msg_parser['msg'].get_bbox_from_list()])
                                #print([i for i in msg_parser['msg'].get_bbox_from_list()])#, '\n context: ', bbox['context'] )
                            except AttributeError:
                                print(msg_parser['msg'])
                        msg_parser['content'] = ''
                        msg_parser['idx'] = 0

        

        #cmd = 'ffmpeg -v fatal -i %s -an -vn -c:s srt -f srt -' % url        
        proc = sp.Popen(cmd,stdout=sp.PIPE)
        self.proc = proc
        time_start = time.time()
        
        while True:
            try:
                raw_msg = proc.stdout.readline().strip().decode()           
            except ValueError as e:
                return 0
            if proc.poll() is not None:
                break
            if raw_msg:
                #print(0,raw_msg)                
                time_duration = time.time() - time_start
                parse(raw_msg,time_duration)          
                if msg_parser['msg'] != '':
                    q.put(['bbox',msg_parser['msg']])
                time_start = time.time()
            rc = proc.poll()


    def cvIdleHandler(self):
        
        if not self.isCVStart:
                if self.is_cvIdle:
                    self.cvIdle_time  = time.time() - self.cvIdle_start_time 
                    #print(self.cvIdle_time)
                    if self.cvIdle_time > 5:
                        self.is_cvIdle = False                                                
                        sys.exit('exit 0 system timeout')       
                else:
                    self.is_cvIdle = True
                    self.cvIdle_start_time = time.time()

    def drawbboxlist(self, fr, bbox_list):
        #print(0,bbox_list)
        for box in bbox_list.get_bbox_from_list():
            sx, sy, ex, ey = box
            cv2.rectangle(fr,(sx,sy),(ex,ey),self.COLOR['GREEN'],3)

    def putText(self,fr,context):
        
        cv2.putText(
            fr,
            context,             
            self.fontFormat['bottomLeftCornerOfText'],
            self.fontFormat['font'],
            self.fontFormat['fontScale'],
            self.fontFormat['fontColor'],
            self.fontFormat['thickness'],            
            self.fontFormat['lineType']
            )    
    """
    #deprecated

    def caprefresh(self):       
        if not self.cap.isOpened():
            print('cap is not opened')
        else:
            self.cap.release()       
        
        self.cap = cv2.VideoCapture(self.localudp)
        if not self.cap.isOpened():
            sys.exit('exit -1 cannot open %s' % self.localudp)

    def test_fn(self,a, b, q):
        
        #test function for threading and queue
        
        # pause a random number of seconds before doing anything else
        time.sleep(random.random())

        # put a message on the queue
        q.put(["{0} {1}".format(a, b)])
    """
    

class THREAD:

    def __init__(self,run):
        self.q = [queue.Queue(),queue.Queue()]        
        self.thread = {}
        self.run = run

    def create_config(self,url):

        pthread = threading.Thread
        self.thread[1] = pthread(target=self.run.srt_fn, args=(url,self.q[0]))
        self.thread[2] = pthread(target=self.run.cv_fn, args=(url,self.q[1]))
        
        # testing threading function below
        #self.thread[3] = pthread(target=self.run.test_fn, args=(1, "john", self.q))
        #self.thread[4] = pthread(target=self.run.test_fn, args=(2, "paul", self.q))       

    def daemon_thread(self):
        self.thread[1].daemon = True
        self.thread[2].daemon = True
        #self.thread[3].daemon = True
        #self.thread[4].daemon = True

    def start_thread(self):
        self.thread[1].start()
        self.thread[2].start()
        #self.thread[3].start()
        #self.thread[4].start()



def main(args):
    
    # initialize parameters
    #url = 'rtsp://192.168.33.147:8554/test.mkv'
    url = args.url
    
    run = RUN()
    # make 2 threads, which will all end up calling the same function
    thread_ = THREAD(run)
    thread_.create_config(url)
    # making a thread a `daemon` means that when the main process
    # ends the thread will end too
    thread_.daemon_thread()
    # start the threads running
    thread_.start_thread()

    cv2.namedWindow(url,cv2.WINDOW_NORMAL)   

    while True:
        
        # if there is any message on the queue, print it.
        # if the queue is empty, the exception will be caught
        # and the queue polled again in a moment

        try:
            msg_mark, msg = thread_.q[0].get(False)
        except queue.Empty:
            pass
        try:            
            fr_mark, fr = thread_.q[1].get(False)    
            thread_.run.isCVStart = False
            try:
                if msg is not None:
                    if thread_.run.verbose==3:                                       
                        thread_.run.drawbboxlist(fr,msg)
                    elif thread_.run.verbose==1:
                        thread_.run.putText(fr,msg)
            except NameError as e:
                #print(e)
                pass
            except AttributeError as e:
                #print(e)
                pass

            cv2.imshow(url,fr)
            thread_.run.is_cvIdle = False
            k = cv2.waitKey(1)            
            if k==ord('q'):
                sys.exit('exit 0 system exits by pressing key q')   
        except queue.Empty:
            # take care of idle too long for the thread
            # or not able to get frame        
            thread_.run.cvIdleHandler()      
                
            

if __name__ == '__main__':
    main(args)