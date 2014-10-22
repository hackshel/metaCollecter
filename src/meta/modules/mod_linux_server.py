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
try:
    import subprocess
    py_ver = True
except:
    py_ver = False


class  State( object ):

    def __init__(self,args=None):
        if not args:
            pass #添加默认参数信息
        else:
            self.args = args

        self.cpu = '/proc/cpuinfo'
        self.mem = '/proc/meminfo'
        self.cmdPath = '/usr/sbin/'

    def search( self,path,cmd,args):
        _cmdPath = [ path, '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args

    def getModel( self ):

        model = ''
        try:
            cmd = self.search( self.cmdPath,'dmidecode',' -s system-product-name')
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

        model = ' '.join( tmp )

        return {'model':model.strip()}

    def getCPU( self ):

        cpuCoreCount=0
        cpuCount=0
        cpuModel=[]
        L1=[]
        cpuCores = []
        siblings = []

        try:
            cmd = self.search( '','cat', ' ' + self.cpu )
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

        for line in tmp:
            i=line.strip('\n')
            if re.match(r'^processor',i):
                cpuCoreCount=cpuCoreCount+1
            elif re.match(r'^physical id',i):
                L1.append(i)
            elif re.findall('model name',i):
                cpuModel.append ( '#'.join(i.split(':')[1].split() ) )
            elif re.match(r'^cpu cores', i ):
                cpuCores.append(i.split(':')[1].strip());
            elif re.match(r'^siblings', i ):
                siblings.append(i.split(':')[1].strip())
            else:
                pass

        #for num in Counter(L1).keys():

        for num in set( L1 ) :
            cpuCount=cpuCount+1
        # check HT (hyper-threading) is enable or Disable
        if len(cpuCores) > 0 and len(siblings) > 0 :
            if cpuCores[0] == siblings[0] :
                cpuHT = 'Disable'
            else:
                cpuHT = 'Enable'
        else:
            cpuHT = ''


        return { 'cpu_numbers':cpuCount,'cpu_cores':cpuCoreCount,'cpu_model':cpuModel[0].strip() , 'cpuHT':cpuHT }


    def getMem( self ):

        L={}
        try:
            cmd = self.search( self.cmdPath,'dmidecode',' -t memory' )
            if py_ver == False:
                os.popen( cmd )
                tmp = n.readlines()
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )
                result = p.communicate()[0]
                if p.returncode == 0:
                    memMax = [ x for x in result.split('\n') ]
                else:
                    memMax = []
        except:
            memMax = []

        if len(memMax ) != 0 :
            for R1 in memMax:
                if re.findall('Maximum',R1):
                    sw,se=R1.split(":")
                    L['mem_max'] = ( se )
        else:
            L['mem_max'] = ''


        try:
            cmd = self.search( '' , 'cat' , ' /proc/meminfo' )
            if py_ver == False:
                m = os.popen( cmd )
                mem = m.readlines()
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )
                result = p.communicate()[0]
                if p.returncode == 0:
                    mem = [ x for x in result.split('\n') ]
                else:
                    mem = []
        except:
            mem = []

        for line in  mem :
            i = line.strip('\n')
            if re.match(r'MemTotal',i):
                m1,m2,m3=line.split()
                L['mem_total'] = str ( int(m2)/1000/1000 ) + 'G'
            if re.match(r'SwapTotal',i):
                sw1,sw2,sw3=line.split()
                L['swap_total'] = str( int (sw2)/1024 ) + 'M'

        return L

    def getPack( self ):

        d = {}
        try:
            cmd = self.search('', 'rpm' ,' -qa|grep sina-watchagent' )
            if py_ver == False:
                p = os.ponpen( )
                pack = p.readlines()
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )

                result = p.communicate()[0]
                if p.returncode == 0:
                    pack = [ x for x in result.split('\n') ]
                else:
                    pack = []
        except:
            pack = []

        t = []

        for line in  pack:
            t.append( line.strip('\n') )

        d['pack'] = ';'.join( t )

        return  d

    def get( self ):

        model = self.getModel()
        cpu   = self.getCPU()
        mem   = self.getMem()
        pack  = self.getPack( )

        r = dict( model )
        r.update( cpu )
        r.update( mem )
        r.update( pack )
        return r


if __name__ == '__main__':

    o = State()

    pprint.pprint( o.get() )
