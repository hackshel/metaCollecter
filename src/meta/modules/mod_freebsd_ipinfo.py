#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import subprocess
import pprint
import os

#from util import core


class State( object ):


    def __init__( self ,args=None ):

        if not args:
            pass #添加默认参数信息
        else:
            self.args = args

        self.cmdPath = '/sbin/'


        self.ip4Re = re.compile("\s*inet\s*([\d]*\.[\d]*\.[\d]*\.[\d]*)")
        self.ip6Re = re.compile("\s*inet6\s*addr:\s*(([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4})")
        self.macRe = re.compile("\s*ether\s*(([0-9a-fA-F]{2})(([/\s:-][0-9a-fA-F]{2}){5}))")


    def search( self,path,cmd,args):
        _cmdPath = [ path, '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args



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


            # 将列表分裂，做成相应的子列表
            for x in tmp:
                end += 1
                if x.startswith('\t') == False:
                    if start == end :
                        pass
                    else:
                        rr.append( tmp[start:end] )
                        start = end


            # 删除lo 回环地址
            for xx in rr:
                if xx[0].startswith('lo'):
                    rr.remove( xx )

            for r in rr :
                #pprint.pprint( r )
                d = {'ipv4':'','ipv6':'','mac':''}

                for s in r:
                    ip4 = self.ip4Re.search( s )
                    ip6 = self.ip6Re.search( s )
                    mac = self.macRe.search( s )
                    if s.startswith('\tmedia'):
                        try:
                            d['speed'] =  s.split(' ')[3].split('(')[1]
                        except:
                            d['speed'] = ''

                    if ip4: d['ipv4'] = ip4.groups()[0]
                    if ip6: d['ipv6'] = ip6.groups()[0]
                    if mac: d['mac'] = mac.groups()[0]

                if d['ipv4'] == '' and d['ipv6'] == '':
                    pass
                else:
                    res.append( d )

            return res
        else:
            return []


    def get( self ):
        return self.getIP()

if __name__ == '__main__':

    o = State()
    print o.get()
