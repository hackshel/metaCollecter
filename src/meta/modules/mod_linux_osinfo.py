#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

class State( object ):

    def __init__( self ,args=None ):

        if not args:
            pass #添加默认参数信息
        else:
            self.args = list(args)

        self.rel = '/etc/redhat-release'
        self.verRe = re.compile("^(\d+(\.\d+)?)")


    def getRelease( self ):

        fp =  open( self.rel )
        c = fp.readlines()
        if c[0] != '':
            line =  c[0].split()
        fp.close()

        r = []

        r.append(line[0].strip())
        for x in line:
            version = self.verRe.search( x )
            if version :
                r.append(version.groups()[0])
                break

        return r

    def get( self ):

        res = {}
        release = self.getRelease()
        res['os_type'] =  self.args[0]
        res['os_kernel'] = self.args[2]
        res['os_platform'] = self.args[4]
        res['os_release'] = release[0]
        res['os_version'] = release[1]
        res['os_hostname'] = self.args[1]

        return res


if __name__ == '__main__':

    o = State( os.uname() )
    print o.get()
