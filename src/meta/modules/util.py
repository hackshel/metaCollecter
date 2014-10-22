import os
import os.path
import pprint
import sys


from os.path import basename
from urlparse import urlsplit
import urllib2
import httplib
import time




def serverInfoLoader(  file ):

    rr = []
    try:
        fp = open( file , 'r' )
        o = fp.xreadlines()
        for r in o :
            ds  = eval(   r.split('\n')[0]  )
            rr.append( ds )

        if len( rr ) ==0:
            return rr
        else:
            return rr[0]

    except IOError:
        return False

def clientOSType():

    clientos = os.uname()
    return clientos


def serverInfo( osTuple ):

    ret = {}

    if osTuple[0] == 'Linux':
        import mod_linux_server as server
        import mod_linux_osinfo as info
        import mod_linux_ipinfo as ips
        import mod_linux_sn as sn
        import mod_linux_disk as disk
        import mod_linux_route as route
    if osTuple[0] == 'FreeBSD':
        import mod_freebsd_server as server
        import mod_freebsd_osinfo as info
        import mod_freebsd_ipinfo as ips
        import mod_freebsd_sn as sn
        import mod_freebsd_disk as disk
        import mod_freebsd_route as route


    s = server.State()
    o = info.State( osTuple )
    p = ips.State()
    _sn = sn.State()
    _disk = disk.State()
    _route = route.State()

    ret['server'] = s.get()
    ret['os']     = o.get()
    ret['ips']    = p.get()
    ret['sn']     = _sn.get()['sn']
    ret['an']     = _sn.get()['an']
    ret['disk']   = _disk.get()
    ret['route']   = _route.get()

    return ret


def wirteToDataFile( filename ,result ):

    try:
        fp = open( filename ,'w' )
        fp.write( str(result) )
        fp.close()
    except:
        return False

def identicalCheck( source , target ):

    change = {}
    for k in source['os'] :
        if source['os'][k] != target['os'][k]:
            change['os'] = target['os']
            break

    for k in source['server']:
        if source['server'][k] != target['server'][k]:
            change['server'] = target['server']
            break

    if len(source['ips']) != len(target['ips']):
        change['ips'] = target['ips']
    else:
        for k in source['ips']:
            for t in target['ips'] :
                if k['mac'] == t['mac']:
                    if k['ipv4'] != t['ipv4'] or k['ipv6'] != t['ipv6']:
                        change['ips'] = target['ips']
                        break

    #TODO add disk check for changes


    if len( source['disk']['raid'] ) != len( target['disk']['raid'] ):
        change['disk'] = target['disk']

    if len( source['disk']['size']) != len( target['disk']['size']):
        change['disk'] = target['disk']

    if not change:
        return True
    else:
        return change

def clearFile( filename ):

    if os.path.exists(filename):

        try:
            fp = open( filename, 'w')
            fp.truncate()
            fp.close()
        except:
            return False


def post( host, port , url , body, header ):
    header['conent-length'] = len(str(body))
    conn = httplib.HTTPConnection( host, port )
    conn.request( 'POST' , url , str(body) , header )
    response = conn.getresponse()
    if response.status == 200:
        res = response.read()
        try:
            return eval(res)
        except:
            return {}

    else:
        return {'state': response.status }

def updateModule( host ,port , url , fileName ):

    conn = httplib.HTTPConnection( host, port )
    conn.request( 'GET' , url +'?filename=' + fileName )
    response = conn.getresponse()
    if response.status == 200:
        res = response.read()
        if len( res ) == 0:
            return  False
        else:
            try:
                fp = open( fileName , 'w')
                fp.write( res )
                fp.close()
                return True
            except:
                return False
    else:
        return False




if __name__ == '__main__':

    POST_HOST = '10.210.66.81'
    POST_PORT = 10086
    POST_URL = '/post_serverinfo'
    POST_HEADER = { 'Content-type' : 'application/x-www-form-urlencoded','Accept' : 'text/json'}

    ret = post( POST_HOST,POST_PORT , POST_URL , 'data='+str(serverInfo) , POST_HEADER )

