# -*- coding: utf-8 -*-
from modules import cmdbServer
from modules import fileHandle
import conf.cmdb_config as conf


class WebServer( object ):


    def __init__( self ):
        pass

    # user(people)  call . get one Server base info
    # data sourece , local file , @path  collectData/

    # 实时回传主机信息，调用 reload 命令
    def getServerFileData( self , ans):
        pass

    # 调用通道接口，下发指令，让主机自己发送数据到webserver
    def getServerData( self , srv ,  action ):

        res = tunnel.get( srv , 'sudo python /usr/local/meta/metaCollecter.py '+ action )

        if type( res ) == types.UnicodeType:
            try:
                return eval( res )
            except:
                return {'err':res}
        else:
            return res


    # client call. write file by sigle file for a server.
    def writeDataFile( self , client_data ):
        pass


    def SourceFileHandle( self , num ,conditions , path , fileName ):

        cmdb = cmdbServer.cmdb( args=conf.CMDBAPI , info=None )
        total = cmdb.search( 'rack_server' , True, 0, 1 , conditions )
        if total % num == 0 :
            times = total / num
        else:
            times = total / num + 1

        #print 'servers total is ' + str(total) + ', run '+ str(times) + '.'

        wfile = fileHandle.WorkProfile( )

        wfile.cleanFile( path , fileName )

        start = 0

        for i in range( times  ) :

            #print 'run time ' + str(i+1)

            res = cmdb.search( 'rack_server' , False, start, num , conditions )
            start =  start + num

            content = ''

            for r in res :
                #content +=  r['asset_number'] +"\t"+ r['ips'] + "\n"
                content +=  r['asset_number'] +"\t"+ r['sn'] +"\t"+ r['rack'].split('.')[0].strip() +"\t"+ r['ips'] + "\n"
                #content +=  ("{'an':"+r['asset_number'] +",'sn':"+ r['sn'] +",'rack':"+ r['rack'].split('.')[0].strip() +",'ips':"+ r['ips'] + "},\n" )

            wfile.writeFile( path , fileName, content )




if __name__ == '__main__':

    fcgi =  WebServer( )

    conditions = [
                    #{'name':'rack','tag':'~','value':r'永丰'},
                    {'name':'state','tag':'~','value':r'在线'}
                 ]
    num = 100


    fcgi.SourceFileHandle( num , conditions , 'sourceData' , 'servers.txt' )

