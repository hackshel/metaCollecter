# -*- coding: utf-8 -*-
import httplib
import urlparse
import urllib
import pprint
import json
import sys
import logging
import types
import MySQLdb
import datetime

#module of own
#import genlog
#import util
#import deviceinfo

import os
from lib import easysql


class materupdater( object ):


    def __init__( self, args , info , an ):

        self.res = {}
        self.result = {}
        self.info = info
        self.args = args
        self.an = an['an']


        self.device_type = '机架服务器'

        self.conn = httplib.HTTPConnection( self.args['host'],self.args['port'] , timeout=10 )

        self.rackServer = self.searchRackServer(  self.an )

        if self.rackServer == {}:
            self.status = 'rack server not found in CMDB by AN : %s' % self.an
            self.cc = False
        else:
            self.result = self.dataFormat( info , self.rackServer )
            self.status,self.cc = self.replaceRackServer( self.rackServer, self.result ,self.an )
            self.logger( 'info', self.status )


    def searchRackServer( self, an ):

        rr = {}
        url = self.args['baseURL']+'username='+self.args['user']+'&auth='+self.args['key']+'&q=asset_number==' +  an
        print url
        #self.conn.connect()
        #self.conn.set_debuglevel( 3 )

        self.conn.request( 'GET', url ,'',self.args['headers'] )
        res = self.conn.getresponse(  )

        if res.status == 200 :
            rs = json.loads( res.read())
            
            try:
                if len( rs['result'] ) != 0 :
                    rr = rs['result'][0]
                else:
                    self.logger('info' , 'Search:  rack server %s is not in cmdb ' % an)
            except:
                pass
        else:
            self.logger('info', an +  'bad request' )

        self.conn.close()

        return rr


    def logger( self, level , loginfo ):

        dt = datetime.datetime.now()
        ds = dt.strftime('%Y%m%d%H%M%S')

        logfile = ds + self.args['logfile']

        logging.basicConfig( filename = os.path.join(os.getcwd()+self.args['logPath'],logfile),
                             level = logging.WARN,
                             filemode = 'w',
                             format = '%(asctime)s - %(levelname)s: %(message)s'
                            )



        if level == 'info': logging.info( loginfo )
        if level == 'warn' :logging.warning( loginfo )
        if level == 'error' :logging.error( loginfo )



    def dataFormat( self,data,cmdb_node ):

        rr = {}

        if cmdb_node != {}:
            rr['id'] = cmdb_node['.id']
            rr['manifest'] = cmdb_node['.manifest']
            rr['value'] = data
        else:

            rr['id'] = ''
            rr['manifest'] = ''
            rr['value'] = data

        return rr


    def replaceRackServer( self, node, data ,an):

        if node != {}:

            url = self.args['baseURL']+'username='+self.args['user']+'&auth='+self.args['key']
            self.conn.request( 'POST', url ,json.dumps(data) ,self.args['headers'] )
            res = self.conn.getresponse()

            rr =  json.loads( res.read())
            if res.status == 200 and rr['success'] == True:
                return  '%s update OK' % node['asset_number'] ,True
            else:
                return  ('%s update faild, %s ') % (node['asset_number'],res.read() ) , False
            self.conn.close()

        else:
            return ' Replace: Node sn %s not found in cmdb ' % an ,False





def getAns( edb ):

    return edb.sys_os.gets( cols=['an'] ,where={'id':('22184','')})
    #return edb.sys_os.gets( cols=['an'] )

def serverInfo( edb  , an ):

    r = {}
    r['disksize'] = edb.sys_disksize.gets( all , where={'an':an['an'] }  )
    r['ipinfos']  = edb.sys_ipinfos.gets( all , where={'an':an['an'] }  )
    r['os'] = edb.sys_os.gets(  all , where={'an':an['an'] } )
    r['physical_disk'] = edb.sys_physical_disk.gets(  all , where={'an':an['an'] } )
    r['raid'] = edb.sys_raid.gets(  all , where={'an':an['an'] } )
    r['serverAN'] = edb.sys_serverAN.gets(  all , where={'an':an['an'] } )
    r['servers'] = edb.sys_servers.gets(  all , where={'an':an['an'] }  )


    res = {}
    res['mac'] = ''
    mac = []
    for ips in r['ipinfos']:
        if ips['mac'] not in mac:
            mac.append( ips['mac'] )

    res['mac'] = '#'.join(mac)


    try:


        if len( r['physical_disk']) == 0:
            res['hw_harddisk'] = ''
        else:
            harddisk = {}

            for disk in r['physical_disk']:
                if len(disk['size']) >= 10 and disk['size'].endswith('[') :
                    disk['size'] = disk['size'][0: len(disk['size']) - 2 ]

                if harddisk.has_key( disk['size'] ):
                    harddisk[ disk['size'] ] += 1
                else:
                    harddisk[ disk['size'] ] = 1

            xdisk = []
            for k,v in harddisk.items():
                xdisk.append( str(k) +'*'+ str(v) )


            res['hw_harddisk']  = '+'.join(xdisk)

    except:
        res['hw_harddisk'] = ''


    try:

        if len( r['raid'] ) == 0 :
            res['hw_raid'] = ''
        else:
            raid_type = {}

            for raid in r['raid']:

                if raid_type.has_key( raid['level'] ) :
                    raid_type[ raid['level'] ].append( raid['raid_id'] )
                else:
                    raid_type[ raid['level'] ] = [ raid['raid_id'] ]



            xraid = []
            for k,v in raid_type.items():
                if( k.startswith( 'Primary') == False ):
                    pprint.pprint( r['raid'] )
                xraid.append( k +':'+ '&'.join( v ) )

            res['hw_raid'] = '#'.join( xraid )

    except:
        res['hw_raid'] = '';


    try:
        res['os'] = (r['os'][0]['os_type'] +'#'
                +r['os'][0]['os_kernel'] +'#'
                +r['os'][0]['os_platform']+'#'
                +r['os'][0]['os_release'] + '#'
                +r['os'][0]['os_version'] )

    except KeyError:
        res['os'] = ''

    try:
        res['hw_cpu'] = ( r['servers'][0]['cpu_numbers'] +'#'
                   +r['servers'][0]['cpu_cores']
                 )
    except KeyError:
        res['hw_cpu'] = ''

    try:
        res['hw_mem'] = ( r['servers'][0]['mem_total'] )
    except KeyError:
        res['hw_mem'] = ''


    return res


if __name__ == '__main__':

    
    args = { 'logfile': 'materupdater.log',
             'logPath': '/logs',
             'host':'newcmdb.intra.sina.com.cn',
             'baseURL':'/api?',
             'user':'api_collector',
             'key':'38Rq67eVbuI86yfOoSptym32',
             'port':'80',
             'headers': {"Content-type": "application/x-www-form-urlencoded",
                        "Accept": " application/json"
                       }
            }


#    args = { 'logfile': 'materupdater.log',
#             'logPath': '/logs',
#             'host':'10.210.231.41',
#             'baseURL':'/api?',
#             'user':'api_collector',
#             #'key':'f89Bzi9OXw7v28DNw0UY4SIh',
#             'key':'38Rq67eVbuI86yfOoSptym32',
#             'port':'80',
#             'headers': {"Content-type": "application/x-www-form-urlencoded",
#                        "Accept": " application/json"
#                       }
#            }
#


    db = { 'host' : '10.210.66.81',
           'port' : 3306,
           'user' : 'micragent',
           'passwd' : 'sina.com',
           'db' : 'metaDB',
         }


    edb = easysql.Database( db )

    ans = getAns( edb  )

    for an in ans:
        info = serverInfo( edb ,an )
#        #print an
#        pprint.pprint( info )

        for i in range( 3 ):
            MU = materupdater( args ,info ,an )
            print MU.status
            if MU.cc == True:
                break


    print 'all is OK'


