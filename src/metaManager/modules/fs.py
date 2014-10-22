#!/usr/bin/env python2.6
# coding: utf-8

import os, sys 
import threading


def read_file( fn ):
    with open( fn, 'r' ) as f:
        return f.read()

def write_file(fn, fcont):
    with open( fn, 'w' ) as f:
        f.write( fcont )
        f.flush()
        os.fsync( f.fileno() )


lock = threading.RLock()

def atomic_write_file( fn, fcont ):
    lock.acquire()
    try:
        tmpfn = fn + "._tmp_." + str(os.getpid()) + str(hash(fcont))
        write_file( tmpfn, fcont )

        os.rename( tmpfn, fn )
    finally:
        lock.release()


def mkdir_if_not_exist( *paths ):
    path = os.path.join( *paths )
    if not os.path.exists( path ):
        try:
            os.makedirs( path )
        except OSError, e:
            raise

