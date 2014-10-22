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


        self.rel = '/etc/rc.conf'
        self.cmdPath = '/usr/local/sbin/'


    def search( self,path,cmd,args):
        _cmdPath = [ path,'/usr/local/sbin', '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args


    def getAN( self ):

        try:
            fp = open( self.rel )
            lines = fp.readlines()
            for x in lines:
                if x.startswith('SINA_ASSET_TAG'):
                    an = x.split('=')[1]
                    break
            return an
        except:

            return None




    def getSN( self ):

        try:
            cmd = self.search( self.cmdPath,'dmidecode', ' -s  system-serial-number')
            n = os.popen( cmd )
            sn = n.readline().strip()
            return sn
        except:
            return None




    def get( self ):

        r ={}
        r['an'] = self.getAN()
        r['sn'] = self.getSN()
        return r

if __name__ == '__main__':

    o = State()
    pprint.pprint( o.get() )
