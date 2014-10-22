#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import subprocess
import pprint
import os


class State( object ):

    def __init__( self ,args=None ):

        if not args:
            pass #添加默认参数信息
        else:
            self.args = args

        self.dellPath = '/opt/MegaRAID/MegaCli/'
        self.hpPath   = '/opt/compaq/hpacucli/bld/'
        self.df = '/bin/'

    def search( self,path,cmd,args):
        _cmdPath = [ path, '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args



    def getRAID( self ):

        return []

    def getDiskInfo( self ):

        return []

    def getSize( self ):

        try:
            cmd = self.search( self.df,'df', ' -h')
            n = os.popen( cmd )
            tmp = n.readlines()
            rr =[]
            for x in tmp:
                r = {}
                if x.startswith('data'):
                    xx =  x.split()
                    r['point'] = xx[5].strip()
                    r['size'] = xx[1].strip()
                if r :
                    rr.append( r )

            return rr
        except:
            return None

    def get( self  ):

        r = {}
        r['size'] = self.getSize()
        r['raid'] = self.getRAID()
        r['pdisk'] = self.getDiskInfo()
        return r

if __name__ == '__main__':

    o = State()
    pprint.pprint( o.get() )
