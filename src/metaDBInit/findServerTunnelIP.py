# -*- coding: utf-8 -*-
import os
import MySQLdb
import easysql
import httplib
import urllib
import pprint
import json
import datetime
import re
import tunnelCore
import types
import os.path
import logging

def ip_classification( ip ):

    # TODO deprecated
    # TODO Modified
    intraPatterns = ['10\..*','127\..*','192\..*','172\..*']


    s = []
    for ptn in intraPatterns :
        if re.match( ptn , ip ):
            if 'intra' not in s:
                s.append('intra')
        else:

            if 'extra' not in s:
                s.append('extra')

    if 'intra' in s:
        return 'intra'
    else:
        return 'extra'


def ip_forgery( ip):

    extraPatterns = [ '10.54\..*',
                      '10.68\..*',
                      '10.48\..*',
                      '10.52\..*',
                      '10.46\..*',
                      '10.50\..*',
                      '192.168\..*',
                      '10.73\..*',
                      '10.44\..*',
                      '10.71\..*',
                      '10.29\..*',
                      '10.10.10\..*',
                      '10.65.129\..*',
                      '10.67\..*',
                      '10.81\..*',
                      '10.77\..*',
                      '10.75\..*',
                      '10.39\..*',
                      '10.79\..*',
                      '10.83\..*',
                      '10.33\..*',
                      '10.34\..*',
                      '10.13\..*',
                      '10.210\..*'
                   ]




    s = []
    for ptn in extraPatterns:

        if re.match( ptn , ip ):
            if 'extra' not in s:
                s.append('extra')
        else:
            if 'intra' not in s:
                s.append('intra')

    if 'extra' in s:
        return 'extra'
    else:
        return 'intra'



def filter_ip_extra( ip ):
    if ip_classification( ip ) == 'extra':
        return 'extra'
    elif ip_forgery( ip ) == 'extra':
        return 'extra'
    else:
        return 'intra'


def getServers( edb , args ):

    r = edb.cmdb_server_basic.gets( ['an'],limit= str(args['start'])+','+str(args['offset']) )

    return r

def getIPs( edb ,an ):

    r = edb.cmdb_ipinfo.gets( all ,where={'an':an['an'] } )

    return r

def tunnelIPExist( edb, an, ips ):

    r = edb.cmdb_server_tunnelIP.gets( all , where={'an':an['an'] } )
    if not r:
        return False
    else:
        for ip in ips:
            if r[0]['tunnel_ip'] == ip['ipv4']:
                return True



def tunnelIPTest( ip ):

    core = tunnelCore.core( {'method':'sync'})
    r = core.get( ip['ipv4'] , 'uname' )
    print ip['an'],ip['ipv4'] , r

    if type( r ) in (types.DictType ,types.ListType ) :
        if r.has_key('err'):
            return False
    else:
        if r == None:
            return False
        else:
            return True




def storeServerTunnelIP( edb ,an ,ip  ):

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    rr = edb.cmdb_server_tunnelIP.puts([{
                                    'id':'',
                                    'an' : an['an'],
                                    'tunnel_ip':ip['ipv4'],
                                    'ctime':ds
                                    }])

    print rr
    return rr

def filter_extra_ip( ips ):

    extra = []
    intra = []
    for ip in ips:
        if ip_classification( ip['ipv4'] ) == 'extra':
            extra.append( ip )
        else:
            intra.append( ip )

    return { 'extra':extra,'intra':intra }

def main( edb , args ):

    while True:
        ans = getServers( edb ,args )
        for an in ans:
            ips = getIPs( edb ,an )
            ip_groups = filter_extra_ip( ips )
            if len( ip_groups['extra'] ) != 0:
                for ip in ip_groups['extra']:
                    if tunnelIPExist( edb, an, ips ) == False:
                        state = tunnelIPTest( ip )
                        if state :
                            storeServerTunnelIP( edb , an ,ip )
                            break
                    else:
                        print 'an:%s,ip:%s was already added Tunnel IP tables' % (an['an'] , ip['ipv4'])
            else:
                 for ip in ip_groups['intra']:
                    if tunnelIPExist( edb, an, ips ) == False:
                        state = tunnelIPTest( ip )
                        if state :
                            storeServerTunnelIP( edb , an ,ip )
                            break
                    else:
                        print 'an:%s,ip:%s  was already added Tunnel IP tables' % (an['an'] , ip['ipv4'])

#            for ip in ips:
#                #print ip
#                if tunnelIPExist( edb, an, ips ) == False:
#                    state = tunnelIPTest( ip )
#                    if state :
#                        storeServerTunnelIP( edb , an ,ip )
#                        break
#                else:
#                    print 'an:%s,ip:%s is add Tunnel IP tables' % (an['an'] , ip['ipv4'])
        args['start'] += args['offset']
        if len ( ans ) < args['offset']:
            break



if __name__ == '__main__':

    args = {
            'start':0,
            'offset':100
            }


    db = { 'host' : 'localhost',
           'port' : 3306,
           'user' : 'root',
           'passwd' : 'Sina!Puppet!',
           'db' : 'metaDB2',
         }


    edb = easysql.Database( db )


    main( edb, args )

