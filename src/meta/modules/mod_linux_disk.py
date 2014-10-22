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


class TimeoutException( Exception ):
    pass


class State( object ):

    def __init__( self ,args=None ):

        if not args:
            pass #添加默认参数信息
        else:
            self.args = args

        self.dellPath = '/opt/MegaRAID/MegaCli/'
        self.hpPath   = '/opt/compaq/hpacucli/bld/'
        self.df = '/bin/'
        self.manufacturer = self.getManufacturer()

    def search( self,path,cmd,args):
        _cmdPath = [ path, '/sbin/','/bin/','/usr/sbin/','/usr/bin/']
        for _cmd in _cmdPath :
            exist = os.access( _cmd+cmd,os.X_OK )
            if exist :
                return _cmd + cmd + args



    def timeout_handler( self, signum , frame ):
        raise TimeoutException()


    def getManufacturer( self ):

        manufacturer = ''

        try:

            cmd = self.search( '','dmidecode', ' --type chassis' )

            if py_ver == False:
                n = os.popen( cmd )
                tmp =  n.readlines()
            else:

                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )
                res = p.communicate()[0]
                if p.returncode == 0 :
                    tmp = [ x for x in res.split('\n') ]
                else:
                    tmp = []

        except:
            tmp = []

        for x in  tmp :
            xx = x.strip()
            if xx.startswith('Manufacturer'):
                manufacturer = xx.split(':')[1].strip()
                break

        return manufacturer.lower()

    def getRAIDForDell( self ):

        try:

            if py_ver == False:
                n = os.popen( cmd )
                tmp =  n.readlines()
            else:
                cmd = self.search( self.dellPath,'MegaCli64', ' -Ldinfo -Lall -a0')
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )
                res = p.communicate()[0]
                if p.returncode == 0 :
                    tmp = [ x for x in res.split('\n') ]
                else:
                    tmp = []
        except:
            tmp = []

        rr = []

        for x in  tmp :
            r ={}
            if x.startswith('RAID Level'):
                r['level'] = x.split(':')[1].split(',')[0].strip()
            else:
                pass
            if r:
                rr.append(r)
        return rr

    def getRAIDForHP( self ):

        try:

            cmd = self.search( self.hpPath,'hpacucli', ' ctrl all show detail config')


            if py_ver == False:
                n = os.popen( cmd )
                tmp =  n.readlines()
            else:


                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )

                res = p.communicate()[0]
                if p.returncode == 0 :
                    tmp = [ x for x in res.split('\n') ]
                else:
                    tmp = []
        except:
            tmp = []

        rr = []

        for x in tmp:
            r = {}
            if x.strip().startswith('Fault Tolerance'):
                r['level'] = x.split(':')[1].strip()
            if r :
                rr.append( r )

        return rr


    def getDiskInfoForDell( self ):

        result = []

        try:

            cmd = self.search( self.dellPath,'MegaCli64', ' -pdlist -aall')

            if py_ver == False:
                n = os.popen( cmd )
                tmp =  n.readlines()
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )
                res = p.communicate()[0]
                #print result
                if p.returncode == 0 :
                    tmp = [ x for x in res.split('\n') ]
                else:
                    tmp = []

        except:
            tmp = []

        slot = []

        arr = {}

        for x in  tmp :
            r = {}
            s = ''
            if x.startswith('Slot Number'):
                s = x.split('\n')[0].split(':')[1].strip()
                if s not in slot:
                    slot.append(s)
                    r['slot'] = s
                    arr[s] = r
            elif x.startswith('Raw Size') :
                arr[slot[-1]]['size'] = x.split(':')[1].split('GB')[0].strip()
            elif x.startswith('PD Type'):
                arr[slot[-1]]['interface'] = x.split(':')[1].strip()

        for key,val in arr.items():
            result.append( val )

        return result

    def getDiskInfoForHP( self ):

        result = []
        try:


            if py_ver == False:
                n = os.popen( cmd )
                tmp =  n.readlines()
            else:
                cmd = self.search( self.hpPath,'hpacucli', ' ctrl all show detail config')
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )

                res = p.communicate()[0]
                if p.returncode == 0 :
                    tmp = [ x for x in res.split('\n') ]
                else:
                    tmp = []
        except:
            tmp = []


        slot = []

        arr = {}

        for x in  tmp :
            x = x.strip()
            r = {}
            s = ''
            if x.startswith('Bay'):
                s =  x.split('\n')[0].split(':')[1].strip()
                if s not in slot:
                    slot.append(s)
                    r['slot'] = s
                    arr[s] = r
            elif x.startswith('Size'):
                if len(slot) == 0 :
                    pass
                else:
                    arr[slot[-1]]['size'] = x.split(':')[1].strip()
            elif x.startswith('Interface Type') :
                if len( slot ) == 0:
                    pass
                else:
                    arr[slot[-1]]['interface'] = x.split(':')[1].strip()

        for key,val in arr.items():
            result.append( val )

        return result

    def getSize( self ):



        signal.signal( signal.SIGALRM , self.timeout_handler )
        signal.alarm(2)

        try:
            cmd = self.search( self.df,'df', ' -h')

            if py_ver == False:
                n = os.popen( cmd )
                signal.alarm( 0 )

                tmp =  n.readlines()
            else:

                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True )

                pid = p.pid

                result = p.communicate()[0]

                signal.alarm( 0 )

                if p.returncode == 0 :
                    tmp = [ x for x in result.split('\n') ]
                else:
                    tmp = []

            rr =[]
            for x in tmp:
                r = {}
                if x.startswith('/dev'):
                    xx =  x.split()
                    r['point'] = xx[5].strip()
                    r['size'] = xx[1].strip()
                if r :
                    rr.append( r )

            return rr
        except TimeoutException:
            os.kill( pid , 9 )
            return None

    def get( self ):


        r = {}

        if self.manufacturer.startswith('hp'):
            r['raid'] = self.getRAIDForHP()
            r['pdisk'] = self.getDiskInfoForHP()

        elif self.manufacturer.startswith( 'dell' ):
            r['raid'] = self.getRAIDForDell()
            r['pdisk'] = self.getDiskInfoForDell()

        else:
            r['raid'] = self.getRAIDForDell()
            r['pdisk'] = self.getDiskInfoForDell()

        r['size'] = self.getSize()

        return r

if __name__ == '__main__':

    o = State()
    pprint.pprint( o.get() )
