import os
import resource

def daemonize():
    #
    # ensure that all file descriptors are closed
    #
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = 1024

    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:
            pass

    #
    # and then redirect stdin, stdout and stderr to /dev/null
    #
    if (hasattr(os, "devnull")):
        REDIRECT_TO = os.devnull
    else:
        REDIRECT_TO = '/dev/null'

    os.open(REDIRECT_TO, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)

    pid = os.fork()
    
    if pid == 0:
        os.setsid()
        os.chdir('/tmp')
        os.umask(0)
    
        pid = os.fork()
    
        if pid == 0:
            return

    os._exit(0)
