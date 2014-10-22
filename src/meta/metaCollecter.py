import time
import os
import sys
import logging
import re
import pprint
import random
import shutil

from os.path import basename
from urlparse import urlsplit
import urllib2



#1.read source data
#2.get moudles return
#3.check source and return
#4.if changed , return changed value,or return nothing
#5.write newest info to file



os.environ['LANGUAGE'] = 'en_US'
prefixdir = os.path.dirname(os.path.abspath(sys.argv[0]))
sourceDir = os.path.join( prefixdir + '/sourceData' )
serverInfoData = sourceDir + '/serverinfo.txt'

default_mutex_port = 10086

from modules import util
import conf.post_config as cnf

version = '1.2.8'

if __name__ == '__main__':

    info = util.clientOSType()

    serverInfo = util.serverInfo( info )

    source = util.serverInfoLoader( serverInfoData )


    if len(sys.argv)>=2 and sys.argv[1]:
        if sys.argv[1] == 'reload':
            util.clearFile( serverInfoData )
            util.wirteToDataFile( serverInfoData,  serverInfo )
            print serverInfo
        elif sys.argv[1] == 'post':
            for i in range( 3 ):
                #r = random.randint(1,1)
                #time.sleep( r )
                ret = util.post( cnf.POST_HOST, cnf.POST_PORT , cnf.POST_URL , 'data='+str(serverInfo) , cnf.POST_HEADER )
                time.sleep(1)
                if ret.has_key('state') and ret['state'] == 'OK':
                    break

            print ret['state']


        elif sys.argv[1] == 'update':

            try:
                filePath = sys.argv[2]
                updateFile = sys.argv[3]
            except:
                print 'no file to update.'


            if util.updateModule( cnf.POST_HOST , cnf.POST_PORT , '/update_module', updateFile ):
                if filePath == 'conf':
                    upPath = './conf'
                elif filePath == 'modules':
                    upPath = './modules'
                else:
                    upPath = '.'
                shutil.move( updateFile ,  upPath+'/'+ updateFile )

                print 'update file '+ updateFile+' OK'
            else:
                print 'update file '+ updateFile+' Error'

        elif sys.argv[1] == 'version':
            print version

    else:
        result =  util.identicalCheck( source,serverInfo )
        util.wirteToDataFile( serverInfoData,  serverInfo )
        if result == True:
            print None
        else:
            print result

    util.clearFile( 'MegaSAS.log' )


#    info = util.clientOSType()
#
#    serverInfo = util.serverInfo( info )
#
#    source = util.serverInfoLoader( serverInfoData )
#
#    if source == False  or len(source) == 0 :
#        result = serverInfo
#        util.wirteToDataFile( serverInfoData,  serverInfo )
#    else:
#        result =  util.identicalCheck( source,serverInfo )
#        util.wirteToDataFile( serverInfoData,  serverInfo )
#
#    util.clearFile( 'MegaSAS.log' )
#
#    if result != True:
#        print result
#    else:
#        print None
#
