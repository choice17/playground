import io
import msvcrt as ms # for fd magic

import win32api, win32file, win32pipe


class pipe(io.IOBase):

    def __init__(self, name, pipetype='server',
                 openmode = (win32pipe.PIPE_ACCESS_DUPLEX |
                             win32file.FILE_FLAG_OVERLAPPED),
                 pipemode = win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_NOWAIT,
                 maxinstances=255,outbuffersize=1000000,inbuffersize=1000000,
                 defaulttimeout=50, securityattrib=None):
        """ An implementation of a file-like Python object pipe.

        Documentation can be found at
        https://msdn.microsoft.com/en-us/library/windows/desktop/aa365150(v=vs.85).aspx

        """
        self.pipetype = pipetype
        self.name = name
        self.openmode = openmode
        self.pipemode = pipemode
        if pipetype == 'server':
            self.handle = win32pipe.CreateNamedPipe(
                r"\.\pipe\%s" % name,
                # the defaults don't need repeating here
                openmode,
                pipemode,
                maxinstances,
                outbuffersize,
                inbuffersize,
                defaulttimeout,
                securityattrib,
            )
        elif pipetype == 'client':
            # it doesn't matter what type of pipe the server is
            # so long as we know the name
            self.handle = win32file.CreateFile(
                r"\.\pipe\%s" % name,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None,
            )
        self.fd = ms.open_osfhandle(self.handle, 0)
        self.is_connected = False
        self.flags, self.outbuffersize, self.inbuffersize, self.maxinstances =
         win32pipe.GetNamedPipeInfo(self.handle)

    def connect(self): # TODO: WaitNamedPipe ?
        win32pipe.ConnectNamedPipe(self.handle,None)
        self.is_connected = True

    # do this at class level rather than in __init__
    __enter__ = connect  

    def __del__(self):
        print("del initiated")
        try:
            self.write(b'') # try to clear up anyone waiting
        except win32pipe.error: # no one's listening
            pass
        self.close()

    def __exit__(self):
        print("exit started")
        self.__del__()

    # Use docstrings, not comments
    def isatty(self):
        """Is the stream interactive (connected to a terminal/tty)?"""
        return False

    def seekable(self):
        return False

    def fileno(self):
        return self.fd

    def seek(self):
        # I think this is clearer than an IOError
        raise NotImplementedError

    def tell(self):
        # as above
        raise NotImplementedError

    def write(self, data):
        """WriteFileEx impossible due to callback issues."""
        if not self.is_connected and self.pipetype == 'server':
            self.connect()
        # there is no need to compare the __name__ of the type!
        if not isinstance(data, bytes):
            data = bytes(data, 'utf-8')
        win32file.WriteFile(self.handle, data)
        return len(data)

    def close(self):
        print("closure started")
        win32pipe.DisconnectNamedPipe(self.handle)

    def read(self, length=None):
        # Always compare None by identity, not equality
        if length is None:
            length = self.inbuffersize
        resp = win32file.ReadFile(self.handle, length)
        if resp[0] != 0:
            raise __builtins__.BrokenPipeError(win32api.FormatMessage(resp[0]))
        else:
            return resp[1]