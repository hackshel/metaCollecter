# -*- coding: utf-8 -*-
import httplib
import pprint
import json
import sys
import logging
import datetime
import os
import os.path
import codecs


class cmdb( object ):


    def __init__( self, args , info=None  ):

        self.res = {}
        self.result = {}
        self.info = info
        self.args = args


        self.device_type = '机架服务器'

        self.conn = httplib.HTTPConnection( self.args['host'],self.args['port'] , timeout=10 )


    def search( self, manifest,  total ,start , limit , conditions ):

        cond = ''
        for x in conditions:
            cond += '%20and%20'+x['name']+x['tag']+x['value']

        if total :
            limit = 1

        rr = {}
        url = (self.args['baseURL']+'username='+self.args['user']
               + '&auth='+self.args['key']
               + '&num='+str(limit)+'&return_total=1&start='+ str(start)
               + '&q=manifest=='+manifest+cond
              )

        self.conn.connect()

        self.conn.request( 'GET', url ,'',self.args['headers'] )
        res = self.conn.getresponse(  )

        if res.status == 200 :

            rs = json.loads( res.read())
            try:
                if len( rs['result'] ) != 0 :
                    if total :
                        rr = rs['total']
                    else:
                        rr = rs['result']
                else:
                    self.logger('info' , 'Search:  rack server %s is not in cmdb ' % an)
            except:
                pass
        else:
            self.logger('info', an +  'bad request' )

        self.conn.close()

        return  rr

    def update( self ):
        pass

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

if __name__ == '__main__':

    import conf.cmdb_config as conf

    conditions = [
                    {'name':'rack','tag':'~','value':r'永丰'},
                    {'name':'state','tag':'~','value':r'在线'}
                 ]
    num = 100

    cmdb = cmdb( args=conf.CMDBAPI , info=None )
    total = cmdb.search( 'rack_server' , True, 0, 1 , conditions )
    if total % num == 0 :
        times = total / num
    else:
        times = total / num + 1

    print 'servers total is ' + str(total) + ', run '+ str(times) + '.'

    wfile = WorkProfile( )

    start = 0
    for i in range( times  ) :

        print 'run time ' + str(i+1)

        res = cmdb.search( 'rack_server' , False, start, num , conditions )
        start =  start + num

        content = ''

        for r in res :
            content +=  r['asset_number'] +"\t"+ r['sn'] +"\t"+ r['rack'].split('.')[0].strip() +"\t"+ r['ips'] + "\n"

        wfile.writeFile( None , 'servers.txt', content )


