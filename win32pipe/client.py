import win32pipe, win32file

p = win32pipe.CreateNamedPipe(r'\\.\pipe\test_pipe',
    win32pipe.PIPE_ACCESS_DUPLEX ,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
    1, 65536, 65536,300,None)

win32pipe.ConnectNamedPipe(p, None)

data = 'Hello Pipe{}'
i =1
import time
while (True):

	i = i+1
	dat =bytes(data.format(i),'utf-8')

	win32file.WriteFile(p, dat)
	time.sleep(0.1)