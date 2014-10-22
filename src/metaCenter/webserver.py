# -*- coding: utf-8 -*-
import time
import pprint
import json
import gc
import cgi
import httplib
#from wsgiref.simple_server import make_server
import threading
import datetime
import os.path
import os

from modules import cmdbServer
from modules import fileHandle
from modules import tunnelCore
from conf import dbinfo
from modules import easysql
from cStringIO import StringIO
from conf import webserver_config  as web_cnf


import conf.cmdb_config as conf

from flup.server.fcgi import WSGIServer
#from superfcgi.server import FastCGIMaster as WSGIServer


sub_list = [ 'get_server', 'reload_cmdbServer' , 'rewrite_cmdbFile' , 'get_allServers']



def errorlog( server , err ):

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y%m%d%H%M%S')

    logPath = '/logs'

    logfile = 'server' + ds + '.log'

    logging.basicConfig( filename = os.path.join(os.getcwd()+logPath, logfile),
                         level = logging.WARN,
                         filemode = 'w',
                         format = '%(asctime)s - %(levelname)s: %(message)s'
                        )

    if err == 'ok':
        logging.info('Server an :'+ server['an'] + ' ip :'+','.join(server['ips'] ) +',has insert into databases.')
    elif err == 'NoIP':
        logging.error('Server an :'+ server['an'] + ' ip is None! ')
    elif err['err'] == None:
        logging.error('Server an :'+ server['an'] + ' ip :'+','.join(server['ips'] ) +',return is '+ str(err['data']) +'.')
    elif err == '':
        logging.error('Server an :'+ server['an'] + ' ip :'+','.join(server['ips'] ) +',return is NULL .')
    elif err['err'] == 'other':
        logging.error('Server an :'+ server['an'] + ' ip :'+','.join(server['ips'] ) +',return is '+err['data']+'..')
    elif err['err'] == 'unknown':
        logging.error('Server an :'+ server['an'] + ' ip :'+','.join(server['ips'] ) +',return is '+err['data']+'...')
    else:
        logging.error('Server an :'+ server['an'] + ' ip :'+','.join(server['ips'] ) +',has error! error is ==>'+ err['err'] +'.')






def writeSourceFile( fileName , servers ):

    path = './'
    wfile = fileHandle.WorkProfile( )
    wfile.cleanFile( path , fileName )
    content = ''

    for s in servers :
        content +=  r['asset_number'] +"\t"+ r['sn'] +"\t"+ r['rack'].split('.')[0].strip() +"\t"+ r['ips'] + "\n"

    wfile.writeFile( path , fileName, content )


def readServersFile( fileName ):

    servers = []

    with open( fileName , 'r' ) as fp:
        lines = fp.readlines()

        for line in lines:
            d = {}
            r = line.split('\t')
            an = r[0].strip()
            sn = r[1].strip()
            rack = r[2].strip()
            ips = r[3].split('\n')[0]


            d['an'] = an
            d['sn'] = sn
            d['rack'] = rack
            d['ips'] = ips

            servers.append( d )

    return servers






class WebServer( object ):

    def __init__( self ):

        try:
            print 'begin init server List ...'
            self.servers = readServersFile( conf.SITEFILE )
            print 'service is ready ...'
        except:
            print 'Read server list File error ...'

        try:
            self.edb = easysql.Database( dbinfo.dbs['infodb']['r'] )
        except:
            print 'database connection is error '

    def init_response( self, res_id ):
        return str(res_id)+" "+httplib.responses.get(res_id)


    def make_null_response( self,env, start_response ):
        start_response( self.init_response(httplib.OK),[])
        return [json.dumps({})]


    def make_bad_response( self, start_response, err_msg, err_code=0, rsp_code=httplib.BAD_REQUEST ):

        self.logger.error( traceback.format_exc() )
        self.logger.error( repr( err_msg ) )
        start_response(init_response(rsp_code), [])
        return [json.dumps({'code':err_code,'msg':repr(err_msg),data:''})]


    def get_qs( self, env ):

        qs = env['QUERY_STRING'].split('&')
        qs = [ q.split('=',1) for q in qs ] 
        qs = [ tuple(q) if len(q) == 2 else (q[0],True) for q in qs ]
        qs = dict(qs)

        return qs

    def reply_default( self ,env , start_response ):

        status = '200 OK'
        response_header = [('Content-type', 'text/plain')]
        start_response( status , response_header )
        return [u'please add actions \n'.encode('utf-8')]


    def reloadServers( self , env ,start_response ):
        try:
            del self.servers
            self.servers = readServersFile( conf.SITEFILE  )
            result = { 'result' : 'OK' }
        except:
            result = {'result':'reload servers field!'}

        return result

    def reply_get_server( self, env ,start_response ):

        qs = env['qs']
        for srv in self.servers:
            if srv['an'] == qs['an']:
                server = srv
                break

        print server

        result = {}

        status = '200 OK'
        response_header = [('Content-type', 'text/plain')]
        start_response( status , response_header )
        return [json.dumps(result)]



    def checkExists( self, edb , postData ):


        if postData.has_key('an') and postData['an'] != '':
            r = edb.sys_os.gets( all , where={ 'an': postData['an'] } )

            if len( r ) > 0 :
                return True , { 'an' :postData['an'], 'sn':postData['sn'] }
            else:
                return False , ''

        #elif postData.has_key('sn') and postData['sn'] !='' and postData['sn'] != None:

        #    r = edb.sys_os.gets( all , where={ 'sn': postData['sn'] } )

        #    if len( r ) > 0 :
        #        return True
        #    else:
        #        return False

        elif postData.has_key('ips'):
            an ,sn = self.findANbyServerList( postData['ips'] )
            print an , sn
            if an != '':
                r = edb.sys_os.gets( all , where={ 'an': an } )
                if len( r ) > 0 :
                    return True , { 'an':an , 'sn':sn }
                else:
                    return False ,''
            else:
                return False , ''
        else:
            return  False, 'no method to find record '

    def findANbyServerList( self, ips ):

        an = ''
        sn = ''
        if len(ips ) != 0:
            for x in ips:
                if x['ipv4'] != '':
                    for srv in self.servers:
                        if x['ipv4'] == srv['ips']:
                            an =  srv['an']
                            sn = srv['sn']
                            break

        return an, sn

    def getStoredData( self, an):
        pass


    def compareDataWithDB( self, postData ):
        pass


    def updateServerInfo( self.edb , postData , serv )
        pass

    # 接收 post 数据，并且进行存储
    def reply_post_serverinfo( self, env ,start_response ,postData ):


        #self.writeServerInfoFile( postData )

        #serv = self.getServ( postData )

        #test case
        #postData['an'] = ''
        #del postData['ips']
        #postData['sn'] = ''
        #postData['ips'][0]['ipv4'] = '10.75.11.115'

        #isExists , serv = self.checkExists( self.edb ,postData )
        #if isExists :
        #    print 'in db ' , serv
        #else :
        #    print 'not in db' ,serv
            #self.storeServerInfo( self.edb , postData , serv )

        #pprint.pprint( postData )

        status = '200 OK'
        response_header = [('Content-type', 'text/plain')]
        start_response( status , response_header )
        return [json.dumps({'state':'OK'})]


    # 接收主机列表，并保存到管理机中 ./servers/site-servers.txt 文件
    def reply_post_serverList( self , env , start_response , postData ):

        if os.path.exists( conf.SITEFILE ):
            os.remove( conf.SITEFILE )

        with open( conf.SITEFILE , 'w') as fp:
            fp.write( postData )
            fp.close()

        status = '200 OK'
        response_header = [('Content-type', 'text/plain')]
        start_response( status , response_header )
        return [json.dumps({'state':'OK'})]


    def getServ( self , postData ):

        serv = {}
        for server in self.servers:
            if postData['an'] == server['an']:
                serv['an'] = server['an']
                serv['sn'] = server['sn']
                break

        if len(serv) == 0:
            serv['an'] = postData['an']
            serv['sn'] = postData['sn']

        return serv

    def storeServerInfo( self, edb , serverData   ,srv ):

        dt = datetime.datetime.now()
        ds = dt.strftime('%Y-%m-%d %H:%M:%S')

        if serverData.has_key('sn'):
            if serverData['sn'] == None:
                serverData['sn'] = 'undefined'
        else:
            serverData['sn'] = 'undefined'

        # save ip infos
        for ip in serverData['ips']:
            ip['an'] = srv['an']
            ip['sn'] = serverData['sn']
            ip['ctime'] = ds
        r = edb.sys_ipinfos.puts( serverData['ips'] )


        serverData['os']['an'] = srv['an']
        serverData['os']['sn'] = serverData['sn']
        serverData['os']['ctime'] = ds
        serverData['server']['an'] = srv['an']
        serverData['server']['sn'] = serverData['sn']
        serverData['server']['ctime'] = ds

        # save disk data
        if serverData.has_key( 'disk' ):
            if serverData['disk'].has_key('raid') and serverData['disk']['raid'] != None:
                if len(serverData['disk']['raid']) != 0 :
                    for i in range(len(serverData['disk']['raid'])):
                        serverData['disk']['raid'][i]['raid_id'] = i
                        serverData['disk']['raid'][i]['an'] = srv['an']
                        serverData['disk']['raid'][i]['sn'] = serverData['sn']
                        serverData['disk']['raid'][i]['ctime'] = ds

                    r4 =  edb.sys_raid.puts( serverData['disk']['raid'] )

            if serverData['disk'].has_key('size') and serverData['disk']['size'] != None:
                if len( serverData['disk']['size'] ) !=0:
                    for ii in range( len( serverData['disk']['size']) ):
                        serverData['disk']['size'][ii]['an'] = srv['an']
                        serverData['disk']['size'][ii]['sn'] = serverData['sn']
                        serverData['disk']['size'][ii]['ctime'] = ds

                    r5 =  edb.sys_disksize.puts( serverData['disk']['size'] )


            if serverData['disk'].has_key('pdisk') and serverData['disk']['pdisk'] != None:
                if len( serverData['disk']['pdisk']) != 0:
                    for iii in range( len( serverData['disk']['pdisk']) ):
                        serverData['disk']['pdisk'][iii]['an'] = srv['an']
                        serverData['disk']['pdisk'][iii]['sn'] = serverData['sn']
                        serverData['disk']['pdisk'][iii]['ctime'] = ds

                    r6 =  edb.sys_physical_disk.puts( serverData['disk']['pdisk'] )


        # save os info
        rr = edb.sys_os.puts( [serverData['os']] )
        # save server  info
        rrr = edb.sys_servers.puts( [serverData['server']] )

        # save  route , dns and sudoers info 
        if serverData.has_key( 'route' ):

            if serverData['route'].has_key('dns'):
                if len( serverData['route']['dns'] ) != 0:
                    for dns in range( len( serverData['route']['dns'] ) ):
                        serverData['route']['dns'][dns]['an'] = srv['an']
                        serverData['route']['dns'][dns]['sn'] = srv['sn']
                        serverData['route']['dns'][dns]['ctime'] = ds

                    edb.sys_dns.puts( serverData['route']['dns'] )

            if serverData['route'].has_key('route'):
                if len( serverData['route']['route'] ) != 0:
                    for route in range( len( serverData['route']['route'] ) ):
                        serverData['route']['route'][route]['an'] = srv['an']
                        serverData['route']['route'][route]['sn'] = srv['sn']
                        serverData['route']['route'][route]['ctime'] = ds

                    edb.sys_route.puts( serverData['route']['route'] )

            if serverData['route'].has_key('sudoers'):
                if len( serverData['route']['sudoers'] ) != 0:
                    for sudo in range( len( serverData['route']['sudoers'] ) ):
                        serverData['route']['sudoers'][sudo]['an'] = srv['an']
                        serverData['route']['sudoers'][sudo]['sn'] = srv['sn']
                        serverData['route']['sudoers'][sudo]['ctime'] = ds

                    edb.sys_sudoers.puts( serverData['route']['sudoers'] )


        # save default an or sn info
        if serverData.has_key( 'an' ):
            if srv['an'] != serverData['an'] :
                r6 = edb.sys_serverAN.puts( [{'id':'','an':srv['an'],'sn':serverData['sn'],'server_an':serverData['an'],'server_sn':serverData['sn'],'ctime':ds}] )
        else:
                r6 = edb.sys_serverAN.puts( [{'id':'','an':srv['an'],'sn':serverData['sn'],'server_an':srv['an'],'server_sn':serverData['sn'],'ctime':ds}] )

    def reply_update_module( self, env , start_response ):
        updateFile = env['qs']['filename']
        filePath  = web_cnf.UPDATE_PATH + '/' + updateFile
        if os.path.exists(filePath):
            length = os.path.getsize(  filePath  )

            with open ( filePath , 'r' ) as fp:
                content = fp.read()
                fp.close()
        else:
            content = ''
        status = '200 OK'
        response_header = [('Content-type', 'text/plain'),('filename', updateFile )]
        start_response( status , response_header )
        return content


    def writeServerInfoFile( self , data  ):

        an = data['an']
        fileName = conf.COLLECTOR_PATH + '/' + an + '.txt'
        with open ( fileName , 'w' ) as fp:
            fp.truncate()
            fp.write( json.dumps(data) )
            fp.close()

    def work( self , env , start_response ):

        env['qs'] = self.get_qs( env )

        if env['PATH_INFO'] == '/':
            return self.make_null_response( env , start_response )
        else:
            #pprint.pprint( env )
            if env['REQUEST_METHOD'] == 'GET':
                return getattr( self, "reply_" + env['PATH_INFO'][1:] )( env, start_response )
            elif env['REQUEST_METHOD'] == 'POST':
                try:
                    length = int( env.get('CONTENT_LENGTH' , '0') )
                except ValueError:
                    length = 0
                if length != 0 :
                    post = env['wsgi.input'].read( length )
                post = post.split('data=')[1]
                try:
                    post = eval(post)
                except:
                    post = post

                return getattr( self, "reply_" + env['PATH_INFO'][1:] )( env, start_response , post)



if __name__ == '__main__':

    s = WebServer()
    print 'Serving on port 10086 ...'
    httpd = WSGIServer( s.work,
                        #method='prefork',
                        #minspare=50,
                        #maxspare=50,
                        #maxchildren=1000
                        bindAddress=('127.0.0.1',10087),
                      ).run()
    httpd.serve_forever()

