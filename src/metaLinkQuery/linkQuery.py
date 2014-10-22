# -*- coding: utf-8 -*-
#run at python 2.7

import os
import MySQLdb
import easysql
import httplib
import urllib
import pprint
import json
import datetime
import re
import types
import os.path
import logging
import cmdbServer
import cmdb_config as conf
import time


class linkQuery( object ):

    def __init__( self ):
        self.host = '10.13.8.60'
        self.port = '5666'
        self.url  = '/link_query'

        #self.headers =  {   "Content-type": "application/x-www-form-urlencoded",
        self.headers =  {   "Content-type": "application/json",
                            "Accept": "text/plain"
                        }


        self.conn = httplib.HTTPConnection( self.host , self.port  )

        self.cmdb = cmdbServer.cmdb( args=conf.CMDBAPI , info=None )

    def link_query( self, query_type ,sip ):


        if query_type == 'serv_ip':

            result = { 'an' : sip['an'] , 'link' : [] }

            for ip in sip['ips']:

                params = json.dumps({'type': query_type , 'sip': ip })

                self.conn.request( 'POST' ,self.url, params ,self.headers )

                res = self.conn.getresponse()

                if res.status == 200:
                    ret = eval(res.read())
                    if ret['code'] == 0 :
                        msg = eval( ret['msg'])
                        if len( msg ) != 0:
                            for fm in msg:
                                result['link'].append( fm )

            return result


    def splitIPs( self, ips_str ):
        ips = []
        for ip in ips_str.split(';'):
            r =  ip.split('-')
            if r[0] == u'内网' or r[0] == u'外网':
                ips.append( r[1] )
        return ips

    def main( self , num , cmdb_conditions  ):

        #cmdb = cmdbServer.cmdb( args=conf.CMDBAPI , info=None )
        total = self.cmdb.search( 'rack_server' , True, 0, 1 , conditions )
        if total % num == 0 :
            times = total / num
        else:
            times = total / num + 1

        start = 0

        for i in range( times  ) :

            res = self.cmdb.search( 'rack_server' , False, start, num , conditions )
            start =  start + num
            time.sleep( 20 )

            for r in res:
                ips = self.splitIPs( r['ips'] )
                print r['asset_number']
                server = { 'an': r['asset_number'] , 'ips': ips}
                link =  self.link_query( 'serv_ip', server )
                print link
                self.updateLink( link , r )


    def updateLink( self , links , cmdb_server ):

        data = ''

        for link in  links['link']:
            s = ('#').join( link )
            data +=  s + ';'

        result = self.cmdb.dataFormat( data , 'switch0', cmdb_server )

        status = self.cmdb.update( cmdb_server , result , links['an'] )

        print status
        #return status






class linkRecord( object ):

    def __init__( self, edb   ):
        self.edb = edb

    def select ( self ):
        pass
    def insert( self , data , types ):
        if types == 'serv':
            r = self.edb.lnk_servers.puts( data )
        elif types == 'net' :
            r = self.edb.lnk_switchs.puts( data )
        return r
    def update( self ):
        pass
    def delete( self ):
        pass

def dataCovert( data, queryType ):

    s = []

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')


    if queryType == 'serv':

        for i in data:
            d = {}
            d['id'] = ''
            d['server_ip'] =  i[0]
            d['switch_ip'] =  i[1]
            d['switch_port'] = i[2]
            d['ctime'] =  ds
            s.append( d )

    elif queryType == 'net':

        for i in data:
            d = {}
            d['id'] = ''
            d['switch_from'] = i[0]
            d['switch_from_port'] = i[1]
            d['switch_to']    = i[2]
            d['switch_to_port'] = i[3]
            d['ctime'] =  ds
            s.append( d )

    return s


if __name__ == '__main__':


    db = { 'host' : 'localhost',
           'port' : 3306,
           'user' : 'root',
           'passwd' : 'Sina!Puppet!',
           'db' : 'metaDB2',
         }


#    edb = easysql.Database( db )

#    lq = linkQuery()

#    lr = linkRecord( edb )

#    try:
#        server_link = lq.link_query( 'serv_ip' )
#        #server_link = dataCovert( lq.link_query( 'serv_ip' ) , 'serv' )
        #pprint.pprint( server_link )
        #switch_link = dataCovert( lq.link_query( 'net' ) , 'net'  )
#        pprint.pprint( eval(server_link['msg']) )
        #pprint.pprint( switch_link )
#    except:
#        print 'get data from API error'

#    try:
#        r = lr.insert( server_link , 'serv' )
#        print 'server' + r
#    except:
#        print 'server data error or database link error'

#    try:
#        z = lr.insert( switch_link , 'net' )
#        print 'server' + z
#    except:
#        print 'switchs data error or database link error'



    conditions = [
                    {'name':'rack','tag':'~','value':r'永丰'},
                    {'name':'state','tag':'~','value':r'在线'}
                 ]
    num = 100


    link = linkQuery()
    link.main( num , conditions )


