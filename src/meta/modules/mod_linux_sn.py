#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
try:
    import subprocess
    py_ver = True
except:
    py_ver = False
import pprint
import os


class State( object ):

    def __init__( self ,args=None ):

        if not args:
            pass #添加默认参数信息
        else:
            self.args = args


        self.rel = '/etc/sinainstall.conf'
        self.cmdPath = '/usr/sbin/'

    def search( self,path,cmd,args):
        _cmdPath = [ path, '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args

    def getAN( self ):

        try:
            fp = open( self.rel )
            an = fp.readline().strip()
            an = an.split('=')[1].strip()
            return an
        except:
            return None

    def getANDmidecode( self ):

        try:
            cmd = self.search( self.cmdPath,'dmidecode', ' -s chassis-asset-tag')
            if py_ver == False:
                n = os.popen( cmd )
                tmp = n.readlines()
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )

                result = p.communicate()[0]

                if p.returncode == 0 :
                    tmp = [ x for x in result.split('\n') ]
                else:
                    tmp = []
        except:
            tmp = []

        an = ''.join( tmp )
        if an.strip() == '':
            an = None
        else:
            an = an.strip()
        return an

    def getSN( self ):

        try:
            cmd = self.search( self.cmdPath,'dmidecode', ' -s  system-serial-number')
            if py_ver == False:
                n = os.popen( cmd )
                tmp = n.readlines()
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )

                result = p.communicate()[0]
                if p.returncode == 0 :
                    tmp = [ x for x in result.split('\n') ]
                else:
                    tmp = []
        except:
            tmp = []

        sn = ''.join( tmp )
        if sn.strip() == '':
            sn = None
        else:
            sn = sn.strip()

        return sn

    def get( self ):

        an = self.getAN()
        r ={}
        if an != None:
            r['an'] = an
        else:
            san = self.getANDmidecode()
            #if san == None:
            #    r['an'] = ''
            #else:
            r['an'] = an


        sn = self.getSN()
        #if sn != None:
        r['sn'] = sn

        return r

if __name__ == '__main__':

    o = State()

    pprint.pprint( o.get( ) )


