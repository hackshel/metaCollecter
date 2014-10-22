#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess

class State( object ):

    def __init__( self ,args=None ):

        if not args:
            pass #添加默认参数信息
        else:
            self.args = list(args)

    def getRelease( self ):

        fp =  open( self.rel )
        c = fp.readlines()
        if c[0] != '':
            line =  c[0].split()
        fp.close()

        return line

    def get( self ):

        res = {}
        res['os_type'] =  self.args[0]
        res['os_kernel'] = self.args[2]
        res['os_platform'] = self.args[4]
        res['os_release'] = self.args[0]
        res['os_version'] = self.args[2]
        res['os_hostname'] = self.args[1]

        return res


if __name__ == '__main__':

    o = State( os.uname() )
    print o.get()
