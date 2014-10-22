#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import subprocess
import pprint
import os


class WorkNotFound( Exception ):
    """
    Error of No Work Defines
    """
    pass

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
        tmp = os.popen( cmd )
        for x in  tmp.readlines():
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
        tmp = os.popen( cmd )
        for x in tmp.readlines( )[4:]:
            if x.startswith('Internet6:'):
                break

            d = {}
            t = []
            for i in x.split(' '):
                if i != '' :
                    t.append( i )
            try:
                if t[1] != '0.0.0.0':
                    d['route'] = t[0]
                    route.append( d )
            except:
                pass
        return route


    def getSudoer( self ):
        sudoers = []
        try:
            cmd = self.search( '' , 'cat' , ' /usr/local/etc/sudoers' )
            tmp = os.popen( cmd )
        except :
            tmp = ''

        if tmp != '':
            for x in  tmp.readlines():
                t = []
                d = {}

                try:
                    if x.startswith('#') == False and x.startswith('User_Alias') == False and x.startswith('USER_WAIBAO') == False :#and  re.search('ALL=\(ALL\)' , x):
                        if x.startswith('root') == False:

                            line_space = x.split(' ')

                            if line_space[0] == 'Defaults' or line_space[0] == '\n':
                                pass
                            else:
                                for i in line_space:
                                    if re.search('\t' , i ):
                                        for ix in i.split('\t'):
                                            if ix != '':
                                                t.append( ix )
                                    elif i != '':
                                        t.append(i)

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
