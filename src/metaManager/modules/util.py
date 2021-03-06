import os,os.path

if os.name != 'nt' : # can be runned in windows for autodoc
    import fcntl
    import pwd
else :
    fcntl = None
    pwd = None

import fs


class FileLockError( IOError ):
    pass 


def open_lock_file( filename, block = False, returnPID = False ):

    # NOTE: open() truncates the file by default if 'w' is in flags.
    #       Use os.open which does not truncate file  unless os.O_TRUNC
    #       specified.
    fd = os.open( filename, os.O_RDWR | os.O_CREAT )

    try: 
        flag = fcntl.LOCK_EX if block \
                else fcntl.LOCK_EX | fcntl.LOCK_NB

        fcntl.lockf( fd, flag )

        if returnPID:
            return fd
        else:
            return os.fdopen( fd, 'w+r' )

    except IOError as e:
        os.close( fd ) 
        if e[0] == 11:
            # errno is 11 means that lock is occupied by other process
            raise FileLockError( filename )



read_file = fs.read_file
