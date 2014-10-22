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

        self.cmdPath = '/sbin/'
        self.ipmiPath = '/usr/bin/'

    def search( self,path,cmd,args):
        _cmdPath = [ path, '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args


    def getDNS( self ):
        dns = []
        cmd = self.search( '' , 'cat' , ' /etc/resolv.conf' )
        #tmp = os.popen( cmd )
        try:
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

        #for x in  tmp.readlines():
        for x in  tmp:
            d = {}
            if x.startswith('nameserver'):
                try:
                    d['dns'] =  x.split('\n')[0].split(' ')[1].strip()
                except:
                    d['dns'] =  x.split('\n')[0].split('\t')[1].strip()
                dns.append( d )

        return dns

    def getRoute( self ):
        route = []
        cmd = self.search( '' , 'netstat' , ' -nr' )
        #xxx = os.popen( cmd )
        #print xxx.readlines( )[2:]
        try:

            if py_ver == False:
                n = os.popen( cmd )
                tmp = n.readlines( )[2:]

            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )
                result = p.communicate()[0]
                if p.returncode == 0 :
                    tmp = [ x for x in result.split('\n') ][2:]
                else:
                    tmp = []
        except:
            tmp = []

        for x in tmp:
            d = {}
            t = []
            for i in x.split(' '):
                if i != '' :
                    t.append( i )
            if len( t ) != 0:
                if t[1] != '0.0.0.0':
                    d['route'] = t[0]
                    route.append( d )

        return route

    def getSudoer( self ):
        sudoers = []
        cmd = self.search( '' , 'cat' , ' /etc/sudoers' )
        try:
            if py_ver == False:
                n = os.popen( cmd )
                tmp = n.readlines()
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )
                pid = p.pid
                result = p.communicate()[0]
                if p.returncode == 0:
                    tmp = [ x for x in result.split('\n') ]
                else:
                    tmp = []
        except:
            tmp = []

        for x in  tmp:
            t = []
            d = {}
            #print x
            try:
                if x.startswith('#') == False and x.startswith('User_Alias') == False and x.startswith('USER_WAIBAO') == False :#and  re.search('ALL=\(ALL\)' , x):
                   if x.startswith('root') == False and x.startswith('Cmnd') == False and x.startswith('USER_SJ') == False:

                        line_space = x.split(' ')
                        #print line_space
                        if line_space[0] == 'Defaults' or line_space[0] == '\n' or line_space[0] == '':
                            pass
                        else:
                            for i in line_space:
                                if re.search('\t' , i ):
                                    for ix in i.split('\t'):
                                        if ix != '':
                                            t.append( ix )
                                elif i != '':
                                    t.append(i)

                            if t[0].isalnum():
                                try:
                                    if t[2] == 'NOPASSWD:' and t[3] == 'ALL\n':
                                        #print t
                                        passwd = t[2]+t[3].split('\n')[0].strip()
                                    else:
                                        passwd = t[2].split('\n')[0].strip()
                                except:
                                    pass

                                d['user'] =  t[0].strip()
                                d['rights'] = t[1].strip()
                                d['passwd'] = passwd

                                sudoers.append( d )

            except:
                pass

        return sudoers

    def get( self ):

        r = {}
        r['route']  = self.getRoute()
        r['dns'] = self.getDNS( )
        r['sudoers'] = self.getSudoer()
        return r


if __name__ == '__main__':

    o = State()
    pprint.pprint( o.get() )
