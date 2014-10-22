# -*- coding: utf-8 -*-
import os
import os.path
import datetime
import time
import pprint
import subprocess
import shutil
import imitation
import httplib
import json

class monitor( object ):

    def __init__( self ,path , backUpPath ,  fileList ):

        self.path = path
        self.backUpPath = backUpPath
        self.fileList = fileList
        #self.state = False

    def checkCatalogChange( self , path , fileList ):
        result = []
        for f in fileList:
            if os.path.exists( path + f ):
                result.append( True )
            else:
                break
                return False

        return len( result ) == len( fileList )

    def mergeFile( self , path , fileList  ):

        dt = datetime.datetime.now()
        ds = dt.strftime('-%Y-%m-%d-%H_%M_%S')

        backUpFileName = 'result' + ds +'.txt'

        backup_fp =  open( path +  backUpFileName ,  'a+' )

        files = ''
        for f in fileList:
            files += path + f + ' '

        cmd = " cat " + files + " |awk '!a[$2]++{print $1 , $2}' "

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result = p.communicate()[0]
        if p.returncode == 0:
            tmp = [ x for x in result.split('\n') ]

            for x in tmp:
                if x != '':
                    backup_fp.write( x+'\n' )
            backup_fp.close()

        if os.path.exists( path + backUpFileName ):
            return backUpFileName
        else:
            return False


    def backUpFile( self , backUpPath , sourcePath , fileName ):
        shutil.move(path + fileName , backUpPath)
        return fileName

    def deleteFile( self , path, fileList ):
        for x in fileList:
            os.remove( path + x )

    def do( self ):

        status = (None, '')

        #while self.state == False:

        if self.checkCatalogChange( self.path , self.fileList ) :
            #self.state = True
            backupFile =  self.mergeFile( self.path , self.fileList )
            if backupFile != False:
                fxx = self.backUpFile( self.backUpPath, self.path , backupFile )
                self.deleteFile( path,  fileList )
                status = ( True, fxx )
            else:
                status = (False, '' )

        return status

class importCmdbServer( object ):

    def __init__( self , path , fileName ):


        self.path = path
        self.fileName = fileName
        self.fcgi =  imitation.WebServer( )

        self.conditions = [
                            {'name':'state','tag':'~','value':r'在线'}
                          ]
        self.num = 100


    def importCmdb( self ):

        print 'prog init , import rack server info form cmdb...'
        self.fcgi.SourceFileHandle( self.num , self.conditions , self.path , self.fileName )
        time.sleep( 3600 *24 )


    def loadServerFile( self ):
        rs = []
        with open( self.path + '/' + self.fileName , 'r' ) as fp:
            lines = fp.readlines()
            for line in lines:
                r = line.split('\t')
                d = { 'an' :r[0] ,'sn':r[1] , 'site' : r[2] }
                rs.append( d )

            fp.close()
        return rs


class splitPingList( object ):

    def __init__( self, servers , idcList ):

        self.servers = servers
        self.idcList = idcList
        self.result = {}
        #self.initIDCFileSTR()


    def initIDCFileSTR( self ):
        del self.result
        self.result = { }
        for idc in self.idcList:
            self.result[ idc ] = []

        self.result[ 'unknown' ] = []


    def splitFile( self, backupPath , backUpFile ):

        with open( backupPath + backUpFile , 'r' ) as fp:
            lines = fp.readlines( )
            for line in lines:
                an , ip = line.split()
                for x in self.servers:
                    if an == x['an']:
                        d = { 'an' : an ,'sn' : x['sn'] , 'ip' : ip , 'site': x['site'] }
                        if self.result.has_key( x['site'] ):
                            self.result[ x['site'] ] .append( d )
                        else:
                            self.result['unknown'].append( d )
                        break

            fp.close()

        return self.result

class serverDispatch( object ):

    def __init__( self , resultPath , idcList ):

        self.resultPath  = resultPath
        self.idcList = idcList
        self.idcList.append( 'unknown')


        self.managers = [ {'name':'永丰','simple_name':'YF.BJ' ,'ip':'10.75.6.31'},
        #self.managers = [ {'name':'永丰','simple_name':'YF.BJ' ,'ip':'10.210.66.81'},
                {'name':'土城','simple_name':'TC.BJ'  ,'ip':'123.125.106.190'},
                {'name':'七星岗','simple_name':'QXG.GZ'  ,'ip':'10.71.6.46'},
                {'name':'西单','simple_name':'XD.BJ'  ,'ip':'10.55.30.63'},
                {'name':'亦庄','simple_name':'YZ.BJ' ,'ip':'172.16.54.66'},
                {'name':'北显','simple_name':'BX.BJ'  ,'ip':'10.13.8.106'},
                {'name':'沙溪','simple_name':'SX.GZ' ,'ip':'172.16.93.10'},
                {'name':'静安','simple_name':'GA.BJ' ,'ip':'10.69.2.50'},
                {'name':'雍和宫','simple_name':'YHG.BJ' ,'ip':'172.16.35.160'},
                {'name':'华苑','simple_name':'BY.TJ' ,'ip':'10.27.16.21'},
                {'name':'丰台','simple_name':'.FTYD.BJ' ,'ip':'10.17.16.21'}
            ]

    def read( self , resultPath, idc ):
        try:
            with open( resultPath + idc +'.txt' ,'r' ) as fp:
                content = fp.read()
        except:
            content = ''

        return content


    def dispatch( self ):

        headers = {"Content-type": "application/x-www-form-urlencoded",
                  "Accept": " application/json"
                  }
        for idc in self.idcList:
            for manager in self.managers:
                if idc == manager['name']:
                    try:
                        url = '/post_serverList'
                        conn = httplib.HTTPConnection( manager['ip'],10086, timeout=10 )
                        conn.connect()
                        conn.request('POST', url , "data="+self.read(self.resultPath , idc ) ,headers )
                        res = conn.getresponse()
                        if res.status ==  200:
                            print 'dispatch servers to manmger : %s OK' % manager['name']
                    except:
                        print 'connections closed. to manager %s ' % manager['name'] 




if __name__ == '__main__':

    #backUpPath : 备份ping 列表文件目录
    #path: 同步文件目录
    #fileList ： 同步文件列表
    backUpPath = '/data2/COLLECTOR_DATA/backup_Ping_List/'
    path       = '/data2/COLLECTOR_DATA/rsync_ping_list/'
    fileList   = ['cnc_result.txt','telecom_result.txt']

    # cmdb 导出基价服务器信息存储位置和文件名
    serverFilePath = './sourceData'
    serverFileName = 'servers.txt'

    # idc 列表
    idcList = [ '永丰','土城','七星岗','西单','亦庄',
                '北显','沙溪','静安','雍和宫','华苑','丰台']

    #分片后文件路径
    resultPath = '/data2/COLLECTOR_DATA/ping_split_result/'

    # 创建importCmdbServer 对象，并导入列表到内存
    im = importCmdbServer( serverFilePath, serverFileName )

    if os.path.exists(serverFilePath + '/' + serverFileName):
        pass
    else:

        print 'init CMDB server infomations to file....'

        fcgi =  imitation.WebServer( )

        conditions = [
                    {'name':'state','tag':'~','value':r'在线'}
                 ]
        num = 100


        fcgi.SourceFileHandle( num , conditions , 'sourceData' , 'servers.txt' )

    print 'init OK...'

    servers = im.loadServerFile()

    #创建分片对象，初始化idc列表对象
    spl = splitPingList( servers , idcList )
    spl.initIDCFileSTR()

    #创建主monitor 对象
    m = monitor( path , backUpPath , fileList   )

    #创建分发对象
    dp = serverDispatch( resultPath , idcList )

    while True:
        status, filename = m.do()
        if status == True :
            print 'backup OK ...'
            print 'begin split server to site files ...'
            result = spl.splitFile( backUpPath , filename )

            for key , value in result.items():

                if os.path.exists( resultPath + key + '.txt' ):
                    os.remove( resultPath + key + '.txt' )

                with open( resultPath + key + '.txt' , 'w') as fp:
                    for x in value:
                        fp.write( x['an'] +'\t' + x['sn'] + '\t'+ x['site'] + '\t' + x['ip'] + "\n"  )
                    fp.close()

            spl.initIDCFileSTR()

            print 'init , clean data , free memory'

            dp.dispatch( )


        elif status == False :
            print 'faild'

        time.sleep( 60 )
