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


def serverList( args ):

    conn = httplib.HTTPConnection( args['host'],args['port'], timeout=10 )
    url = args['url'] + '?return_total=1&start='+str(args['start'])+'&num='+str(args['num'])+'&q=manifest==rack_server%20and%20state==在线'
    url += '%20and%20product%20!~%20奥委会合作伙伴%20and%20product%20!~%20供保库存%20and%20product%20!~%20新浪show%20and%20product%20!~%20房产%20and%20product%20!~%20游戏%20and%20asset_number%20!~%20HEZUO'

    print url
    conn.request( 'GET', url )
    res = conn.getresponse()

    if res.status == 200:
        ret = json.loads(res.read())
        if  ret['result']:
            return ret['result']

def findIPByServer( element ):

    conn = httplib.HTTPConnection( args['host'],args['port'], timeout=10 )
    url = args['url'] + '?return_total=1&q=manifest==ip_info%20and%20server_asset_number==' + element['asset_number']
    conn.request( 'GET', url )
    res = conn.getresponse()

    if res.status == 200:
        ret = json.loads(res.read())
        if ret['result']:
               return ret['result']



def existCheck( edb, element ):

    r = edb.cmdb_server_basic.gets(all,where={'an':element['asset_number']})

    if not r :
        return None
    else:
        return r


def storeServerBasicInfo( edb, element ):

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    r = edb.cmdb_server_basic.puts([{'id':'',
                                    'cmdb_id':element['.id'],
                                    'an':element['asset_number'],
                                    'sn':element['sn'].encode('utf-8'),
                                    'state':element['state'].encode('utf-8'),
                                    'rack':element['rack'].encode('utf-8'),
                                    'service_type':element['service_type'].encode('utf-8'),
                                    'is_collect':'on',
                                    'ctime':ds
                                    }])
    return r


def ipCheck( edb , an,ip ):

    r = edb.cmdb_ipinfo.gets(all,where={ 'an':an,'ipv4':ip })

    if len(r) == 0 :
        return None
    else:
        return r




def storeIPsBasicInfo( edb , an ,sn,ips ):

    #d = findIPByServer( element )
    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

#    r = []
#    if not d:
#        pass
#    else:
#        for x in d:
#            dr = {}
#            if ipCheck( edb , element['asset_number'], x['ip_name'] ) == None:
#                dr['id'] = ''
#                dr['an'] = x['server_asset_number']
#                dr['sn'] = element['sn']
#                dr['ipv4'] = x['ip_name']
#                dr['ipv6'] = ''
#                dr['ctime'] = ds
#                r.append( dr )
#            else:
#                print '%s ips is in the table.' % ( element['asset_number'] )
#

    rr = edb.cmdb_ipinfo.puts( [{
                                        'id':'',
                                        'an':an,
                                        'sn':sn,
                                        'ipv4':ips['ip_name'],
                                        'ipv6':'',
                                        'ctime':ds
                                    }] )

    return rr


if __name__ == '__main__':


    args = { 'url' : '/search',
             'host': '10.55.38.100',
             'port': '9999',
             'start' : 22000,
             #'start' : 0 ,
             'num' :100
           }


    db = { 'host' : 'localhost',
           'port' : 3306,
           'user' : 'root',
           'passwd' : 'Sina!Puppet!',
           'db' : 'metaDB2',
         }


    edb = easysql.Database( db )

    while True:
        #pprint.pprint( args )
        List = serverList( args )
        for x in List:
            if x['asset_number'].startswith('CESHI') or x['asset_number'].startswith('LJ') or x['asset_number'].startswith('HEZUO'):
                pass
            else:
                #pprint.pprint ( x )
                isExist = existCheck( edb ,x )
                if isExist == None :
                    storeServerBasicInfo( edb , x )
                    print '%s is insert into db.' % ( x['asset_number'] )
                else:
                    print '%s is already exitst.' % ( isExist[0]['an'] )

                ips = findIPByServer( x )
                if ips  != None:
                    for ip in ips:
                        if ipCheck( edb , x['asset_number'] ,ip['ip_name'] ) == None:
                            print ip
                            storeIPsBasicInfo( edb, x['asset_number'],x['sn'], ip )
        #print 'here,add start %s' % args['start']
        args['start'] = args['start'] + args['num']

        if len(List) < args['num']:
            break

