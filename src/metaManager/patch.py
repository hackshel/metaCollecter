# -*- coding: utf-8 -*-
import os
import MySQLdb
from modules import easysql
from modules import tunnelCore
import httplib
import urllib
import pprint
import json
import datetime
import types
import os.path
import logging
import threading
import multiprocessing



#1.get server basic info from sys_server_basic
#2.https call from default server tunnel ip
#3.init will return all data from server,insert it into default tables
#4.check default value if there is change.
#5.insert into orig value to tables,and update new value to databases




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



def getServerData( tunnel ,srv ,action):

    res = tunnel.get( srv , 'sudo python /usr/local/meta/metaCollecter.py '+ action )

    return res

def configure( tunnel , srv , action ):
    res = tunnel.get( srv , 'sudo wget ')
    return res

def main( name , servers , tunnel):

    #pprint.pprint( servers )

    ip = []

    for srv in servers:
        #print srv['an'] , srv['ips'] ,srv['site']

        try:
            ip.append( srv['ips'] )

        except KeyboardInterrupt:

            print 'user cancel'
            break



    print ip
    print len( ip )
    try:
       serverData = getServerData( tunnel , ip , 'post')
       print len( serverData )
       print serverData
    except KeyboardInterrupt:
        print 'user cancel'




    #serverData = getServerData( tunnel , ip , 'reload')
    #print serverData
    #print len( serverData )




if __name__== '__main__':


    tunnel = tunnelCore.core( {'method':'async' } )

    servers = []

    path = '/usr/home/xiaochen2/metaManager/'

    with open( path + 'servers/site-servers.txt', 'r' ) as fp:
        lines = fp.readlines()
        for line in lines:
            server = line.split('\t')
            d = { 'an': server[0] ,'sn' : server[1] , 'site': server[2] , 'ips': server[3].split('\n')[0] }
            servers.append( d );

    maxThread = 100
    minThread = 1

    import random
    for x in range(100):
        random.shuffle( servers )

    total_server = len( servers )
    print total_server


    rr = []

    if total_server < 300:
        evenMax = total_server
        rr.append( servers )
    else:
        evenMax = total_server / maxThread

        if total_server % maxThread >0 :
            evenMax += 1


        for i in range( maxThread ):
            rr.append( servers[evenMax*i:evenMax*(i+1)] )

    print len( rr )
    for r in rr:
        main('name', r , tunnel )


