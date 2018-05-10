"""
import win32pipe, win32file
import win32file
fileHandle = win32file.CreateFile("\\\\.\\pipe\\test_pipe",
                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)

win32pipe.SetNamedPipeHandleState(fileHandle,
                              win32pipe.PIPE_READMODE_MESSAGE, None, None)



a, data = win32file.ReadFile(fileHandle, 4096)
if not a:
	print(data)

"""
import win32pipe
import win32file

file_handle = win32file.CreateFile("\\\\.\\pipe\\test_pipe",
                               win32file.GENERIC_READ |
                               win32file.GENERIC_WRITE,
                               0, None,win32file.OPEN_EXISTING,0, None)
# this is the key, setting readmode to MESSAGE
win32pipe.SetNamedPipeHandleState(file_handle,
                              win32pipe.PIPE_READMODE_MESSAGE, None, None)
# for testing purposes I am just going to write the messages to a file
out_ref = open(r'C:\Users\im147\Desktop\output\aa.txt','w')

dstring = ''  # need some way to know that the messages are complete
#while dstring != 'Process Complete':
    # setting the blocksize at 4096 to make sure it can handle any message I
    # might anticipate
import time
while True:

	a, data = win32file.ReadFile(file_handle,4096)
	if not a:
		print (a,data.decode("utf-8"))
	
# data is a tuple, the first position seems to always be 0 but need to find 
# the docs to help understand what determines the value, the second is the 
# message
#    dstring = data[1]
#    out_ref.write(dstring + '\n')

#out_ref.close() # got here so close my testfile
#file_handle.close() # close the file_handle