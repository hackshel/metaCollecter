#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Gets the memory info of the server.
@author: xiaochen
"""

__author__ = 'xiaochen'
import os
import pprint
import re
import subprocess


class  State( object ):

    def __init__(self,args=None):
        if not args:
            pass #添加默认参数信息
        else:
            self.args = args

        self.cmdPath = '/usr/sbin/'

    def search( self,path,cmd,args):
        _cmdPath = [ path, '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args

    def getModel( self ):
        try:
            cmd = self.search( self.cmdPath,'dmidecode',' -s system-product-name')
            n = os.popen( cmd )
            model = n.readlines()
        except:
            model = ''

        return {'model':model}


    def getCPU( self ):
        try:
            cmd = self.search( self.cmdPath,'sysctl',' -a | grep -Ei "hw.model|hw.ncpu|hw.physmem|machdep.hlt_logical_cpus"')
            n = os.popen( cmd )
            result = n.readlines()
            cpu_numbers = len( [ x for x in result  if x.startswith('hw.model') ] )

            d = {}
            for x in result :
                r = x.split(':')
                d[r[0].strip()] =  r[1].strip()

            cpu_cores = d['hw.ncpu']
            cpu_model = d['hw.model']
            mem_total = d['hw.physmem']
            cpu_HT = d['machdep.hlt_logical_cpus']
            if cpu_HT == 0:
                cpuHT = 'Disable'
            else:
                cpuHT = 'Enable'

        except:
            cpu_cores = ''
            cpu_model = ''
            cpu_total = 1
            cpu_HT = ''

        return { 'cpu_numbers':cpu_numbers,'cpu_cores':cpu_cores,
                 'cpu_model':cpu_model, 'mem_total': str ( int( mem_total )/1000/1000/1000 ) + 'G' , 'cpuHT':cpuHT }



    def getMem( self ):
        try:
            cmd = self.search( self.cmdPath,'dmidecode',' -t memory' )
            memMax = os.popen( cmd )
        except:
            memMax = ''

        L={}
        if memMax != '':
            for line in memMax.readlines():
                R1=line.strip("\n")
                if re.findall('Maximum',R1):
                    sw,se=R1.split(":")
                    L['mem_max'] = ( se )
            memMax.close()

            mem = file( self.mem )

            for line in  mem.readlines():
                i = line.strip('\n')
                if re.match(r'MemTotal',i):
                    m1,m2,m3=line.split()
                    L['mem_total'] = str ( int(m2)/1000/1000 ) + 'G'
                if re.match(r'SwapTotal',i):
                    sw1,sw2,sw3=line.split()
                    L['swap_total'] = str( int (sw2)/1024 ) + 'M'

        else:
            L['mem_max'] = ''
            L['mem_total'] = ''
            L['swap_total'] = ''

        return L

    def get( self ):

        model = self.getModel()
        cpu   = self.getCPU()
        mem   = self.getMem()

        r = dict( model )
        r.update( cpu )
        r.update( mem )
        r['pack'] = ''
        return r


if __name__ == '__main__':

    o = State( )

    pprint.pprint( o.get() )
