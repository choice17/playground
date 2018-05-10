import os
import time
import subprocess as sp
import sys

pipe = sys.argv[1]
#pipe = 'outpipe'
cmd_ = 'cat'
p = sp.Popen([cmd_,pipe], stdout=sp.PIPE)
print(p.communicate())


#fifo_read = open('outpipe', 'rb')
#while True:
#	print(fifo_read.readlines())
#	time.sleep(0.2)

