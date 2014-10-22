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


#0.get last id from db
#1.get server from cmdb
#2.get ips from cmdb
#3.check ips to find tunnel ip
#4.store info to db



def errorlog( element ,ip , ipType):

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y%m%d%H%M%S')

    logPath = '/logs'

    logfile = ds + '.log'

    logging.basicConfig( filename = os.path.join(os.getcwd()+logPath, logfile),
                         level = logging.WARN,
                         filemode = 'w',
                         format = '%(asctime)s - %(levelname)s: %(message)s'
                        )

    if ipType == 'extra':
        logging.warning('Server an :'+ element['asset_number'] + ' ip :'+ip +'is extra ip ,but can not connect server by tunnel.')
    elif ipType == 'intra':
        logging.warning('Server an :'+ element['asset_number'] + ' ips :'+element['ips'] +'all is intra ip,  can not connect server by tunnel.')
    elif ipType == None:
        logging.warning('Server an :'+ element['asset_number']+' has NO ips, can not connect server' )
    elif ip == 'error' and ipType == 'error':
        logging.warning('Server an :'+ element['asset_number']+' is TEST server' )
    else:
        logging.warning('code running is error! ending at start:%s, num:%s' % element , ip )

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

def getMetaCount( edb) :

    result = edb.sys_server_basic2.getCounts('count')
    return result

def getCMDBCount( args ):

    try:
        conn = httplib.HTTPConnection( args['host'],args['port'], timeout=10 )
        url = args['url'] + '?return_total=1&num=1&q=manifest==rack_server%20and%20state==在线'
        conn.request( 'GET', url )
        res = conn.getresponse()
    except:
        res = ''
    if res.status == 200:
        total = json.loads(res.read())['total']
    else:
        total = 'return error'

    return total


def serverList( args ):

    conn = httplib.HTTPConnection( args['host'],args['port'], timeout=10 )
    #url = args['url'] + '?return_total=1&start='+str(args['start'])+'&num='+str(args['num'])+'&order_by=id&order=desc&q=manifest==rack_server%20and%20state==在线'
    url = args['url'] + '?return_total=1&start='+str(args['start'])+'&num='+str(args['num'])+'&order_by=id&order=desc&q=manifest==rack_server%20and%20state==在线'
    url += '%20and%20product%20!~%20奥委会合作伙伴%20and%20product%20!~%20供保库存%20and%20product%20!~%20新浪show%20and%20product%20!~%20房产%20and%20product%20!~%20游戏%20and%20asset_number%20!~%20HEZUO'
    print url
    conn.request( 'GET', url )
    res = conn.getresponse()

    if res.status == 200:
        ret = json.loads(res.read())
        if  ret['result']:
            return ret['result']

def tunnelIPTest( ip ):

    core = tunnelCore.core( {'method':'sync'})
    r = core.get( ip , 'uname' )
    print ip , r

    if type( r ) in (types.DictType ,types.ListType ) :
        if r.has_key('err'):
            return False
    else:
        if r == None:
            return False
        else:
            return True

def findTunnelIp2( element ):

    conn = httplib.HTTPConnection( args['host'],args['port'], timeout=10 )
    url = args['url'] + '?return_total=1&q=manifest==ip_info%20and%20server_asset_number==' + element['asset_number']
    conn.request( 'GET', url )
    res = conn.getresponse()

    if res.status == 200:
        ret = json.loads(res.read())
        if ret['result']:
            for r in ret['result']:
                if filter_ip_extra( r['ip_name']) == 'extra' :
                    if tunnelIPTest( r['ip_name'] )  == True:
                        element['tunnelIP'] = r['ip_name']
                        element['tunnelState'] = 'ok'
                        break
                    else:
                        element['tunnelIP'] = r['ip_name']
                        element['tunnelState'] = 'fail'
                        errorlog( element , r['ip_name'] , 'extra')
                else:
                    element['tunnelIP'] = ''
                    element['tunnelState'] = 'fail'
                    errorlog( element , r['ip_name'] , 'intra')
        else:
            element['tunnelIP'] = ''
            element['tunnelState'] = 'fail'
            errorlog( element , None , None )


    return element


def existCheck( edb, element ):

    #r = edb.sys_server_basic.gets(all,where={'sn':element['sn'],'an':element['asset_number']})
    r = edb.sys_server_basic2.gets(all,where={'an':element['asset_number']})
    if not r :
        return None
    else:
        return r

def storeServerBasicInfo( edb, element ):

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    if element['tunnelIP'] == '':
        is_collect = 'off'
    else:
        if element['tunnelState'] == 'fail':
            is_collect = 'off'
        else:
            is_collect = 'on'


    r = edb.sys_server_basic2.puts([{'id':'',
                                    'cmdb_id':element['.id'],
                                    'an':element['asset_number'],
                                    'sn':element['sn'],
                                    'tunnel_ip':element['tunnelIP'],
                                    'state':element['state'].encode('utf-8'),
                                    'rack':element['rack'].encode('utf-8'),
                                    'service_type':element['service_type'].encode('utf-8'),
                                    'is_collect':is_collect,
                                    'ctime':ds
                                    }])
    return r


if __name__ == '__main__':


    args = { 'url' : '/search',
             'host': '10.55.38.100',
             'port': '9999',
             'start' : 0,
             'num' :100
           }


    db = { 'host' : 'localhost',
           'port' : 3306,
           'user' : 'root',
           'passwd' : 'Sina!Puppet!',
           'db' : 'metaDB',
         }

    edb = easysql.Database( db )

    count = getMetaCount( edb )

    cmdbCount = getCMDBCount( args )

    offset = int(cmdbCount) - int(count[0]['count'])

    print offset

    """
        if offset <0 ,so has some servers was delete from cmdb
        to cmdb queue ,check the delete servers ,delete its from mysql.
        action save at here.
    """

    times =  offset / args['num']
    if offset % args['num'] != 0:
        times += 1
    print times

    if offset == 0 :
        exit()
    else:
        for i in range( times ):
            try:
                List = serverList( args )
                for x in List:
                    print x['asset_number']
                    if x['asset_number'].startswith('CESHI') or x['asset_number'].startswith('LJ') or x['asset_number'].startswith('HEZUO'):
                        errorlog( x ,'error','error' )
                    else:
                        isExist = existCheck( edb , x )
                        if isExist == None:
                            r = findTunnelIp2( x )
                            storeServerBasicInfo( edb , r )
                            print '%s is insert into db.' %( x['asset_number'] )
                        else:
                            print '%s is already exitst.' % ( isExist[0]['an'] )
                args['start'] = args['start'] + args['num']

            except:
                errorlog( args['start'] , args['num'] ,'' )

