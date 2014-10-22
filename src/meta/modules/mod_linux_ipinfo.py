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
import signal
import time

#from util import core


class TimeoutException( Exception ):
    pass

class State( object ):


    def __init__( self ,args=None ):

        if not args:
            pass #添加默认参数信息
        else:
            self.args = args

        self.cmdPath = '/sbin/'
        self.ipmiPath = '/usr/bin/'
        self.ip4Re = re.compile("\s*inet\s*addr:([\d]*\.[\d]*\.[\d]*\.[\d]*)")
        self.ip6Re = re.compile("\s*inet6\s*addr:\s*(([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4})")
        self.macRe = re.compile("\s*Ethernet\s*HWaddr\s*(([0-9a-fA-F]{2})(([/\s:-][0-9a-fA-F]{2}){5}))")


    def search( self,path,cmd,args):
        _cmdPath = [ path, '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args

    def timeout_handler( self, signum , frame ):
        raise TimeoutException()


    def ipmiStart( self ):

        signal.signal( signal.SIGALRM , self.timeout_handler )
        signal.alarm(2)

        try:
            cmd = self.search( self.cmdPath , 'service' , ' ipmi start' )

            if py_ver == False:

                n = os.popen( cmd )

                signal.alarm( 0 )

                tmp = n.readlines()

                if tmp[0].find('OK'):
                    state =  True
                else:
                    state =  False

            else:

                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )

                pid = p.pid

                result = p.communicate()[0]

                signal.alarm( 0 )

                if p.returncode == 0 :
                    tmp = [ x for x in result.split('\n') ]
                    if tmp[0].find('OK'):
                        state =  True
                    else:
                        state =  False
                else:
                    state = False

        except TimeoutException:
            self.getZombieIpmi()
            #os.kill( pid , 9 )
            #pgrp = os.getpgid( pid )
            #print pgrp
            #os.killpg( pgrp , 9 )
            #pgid = os.getpgid( pid )
            #print pgid
            state =  None

        return state


    def getZombieIpmi( self ):

        try:

            cmd = self.search( '', 'ps' , ' -ef | grep ipmi ' )

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

            for x in tmp:
                if len( x ) != 0:
                    pid =  x.split()[1].strip()
                    try:
                        os.kill( int( pid ) , 9 )
                    except OSError:
                        pass
            return True
        except:
            return False

    def getOOBIP( self ):

        ipmiState = self.ipmiStart()

        if ipmiState:
            try:
                cmd = self.search( self.ipmiPath , 'ipmitool' , ' lan print' )

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

                d = {'ipv4':'','ipv6':'','mac':''}

                for x in tmp:
                    if x.startswith('IP Address   '):
                        d['ipv4'] =  x.split(':')[1].strip()
                    if x.startswith('MAC Address'):
                        r = x.strip().split(':')
                        r = ':'.join(r[1:]).strip()
                        d['mac'] = r
                        d['speed'] = ''

                return d
            except:
                return None
        else:
            return None


    def getSpeed( self , eth ):
        try:
            if eth == 'eth0' or eth == 'eth1':
                cmd = self.search( self.cmdPath , 'ethtool' ,' '+eth )
                if py_ver == False:
                    p = os.popen( cmd )
                    tmp = p.readlines()
                else:
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )

                    result = p.communicate()[0]
                    if p.returncode == 0 :
                        tmp = [ x for x in result.split('\n') ]
                    else:
                        tmp = []

                for x in tmp :
                    if x.startswith('\tSpeed'):
                        return x.split(':')[1].split('\n')[0].strip()
            else:
                return ''
        except:
            return None



    def getIP(self):
        """获取本机内外网ip,去除回环地址
        XXX: only for linux because dev only eth"""
        cmd = self.search( self.cmdPath,'ifconfig','' )
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.communicate()[0]
        if p.returncode == 0:

            tmp = [ x for x in result.split('\n') ]
            rr = []
            res = []
            start = 0
            end = -1
            dr = []
            # 将列表分裂，做成相应的子列表
            for x in tmp:
                end += 1
                if x == '':
                    if start == end :
                        break

                    rr.append( tmp[start:end] )
                    start = end + 1

            #pprint.pprint( rr )

            # 删除lo 回环地址
            for x in range( len(rr) ) :
                if rr[x][0].startswith('lo') == False:
                    dr.append(rr[x])

            #pprint.pprint( dr )

            for r in dr :
                #pprint.pprint( r )
                d = {'ipv4':'','ipv6':'','mac':''}
                for s in r:
                    ip4 = self.ip4Re.search( s )
                    ip6 = self.ip6Re.search( s )
                    mac = self.macRe.search( s )
                    try:
                        if s.startswith( 'eth' ):
                            d['speed'] = self.getSpeed( s.split(' ')[0] )
                    except:
                        d['speed'] = ''

                    if ip4: d['ipv4'] = ip4.groups()[0]
                    if ip6: d['ipv6'] = ip6.groups()[0]
                    if mac: d['mac'] = mac.groups()[0]

                    #res.append( d )
                #pprint.pprint ( d )
                if d['ipv4'] == '' and d['ipv6'] == '':
                    pass
                else:
                    res.append( d )

            return res
        else:
            return []

    def get( self ):


        ips = self.getIP()

        oob = self.getOOBIP()
        if oob != None:
            ips.append( oob )


        return ips

if __name__ == '__main__':

    o = State()
    pprint.pprint( o.get() )
