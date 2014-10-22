# -*- coding: utf-8 -*-
import os
import MySQLdb
from lib import easysql
from lib import tunnelCore
import httplib
import urllib
import pprint
import json
import datetime



#1.get server basic info from sys_server_basic
#2.https call from default server tunnel ip
#3.init will return all data from server,insert it into default tables
#4.check default value if there is change.
#5.insert into orig value to tables,and update new value to databases


def loadServerBasic( edb ,args ):

    res = edb.cmdb_server_basic.gets(['an','sn','is_collect'],where={'is_collect':'on'} , limit= str(args['start'])+',' + str(args['offset']) )
    return res

def loadServerTunnelIP( edb , an ):

    r = edb.cmdb_server_tunnelIP.gets( ['an','tunnel_ip'] , where={'an':an })
    return r

def loadOriginalData( edb ,srv ):

    d = {}
    ips = edb.sys_ipinfos.gets( all , where={'an':srv['an'],'sn':srv['sn']} )
    osInfo = edb.sys_os.gets( all , where={'an':srv['an'],'sn':srv['sn']} )
    srvInfo = edb.sys_servers.gets( all , where={'an':srv['an'],'sn':srv['sn']} )
    raidInfo = edb.sys_raid.gets( all , where={'an':srv['an'],'sn':srv['sn'] } )
    disksize = edb.sys_disksize.gets( all , where={'an':srv['an'],'sn':srv['sn'] } )

    if len(ips) != 0:
        d['ips'] = ips
    if  len(osInfo) != 0:
        d['os'] = osInfo[0]
    if len(srvInfo) != 0:
        d['server'] = srvInfo[0]
    if len( raidInfo )  != 0:
        d['raid'] = raidInfo
    if len( disksize ) !=0:
        d['disksize'] = disksize

    return d


def getServerData( tunnel ,srv ,action):

    #res = tunnel.get( srv['tunnel_ip'] , 'sudo python metaCollecter.py ' + action + ' 2>&1')
    res = tunnel.get( srv['tunnel_ip'] , 'sudo python /usr/local/meta/metaCollecter.py '+ action )
    return res

def storeServerInfo( edb , serverData , srv ):

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    serverData =  eval(serverData)
    #pprint.pprint( serverData )
    #ips = serverData['ips']
    for ip in serverData['ips']:
        ip['an'] = srv['an']
        ip['sn'] = srv['sn']
        ip['ctime'] = ds
    serverData['os']['an'] = srv['an']
    serverData['os']['sn'] = srv['sn']
    serverData['os']['ctime'] = ds
    serverData['server']['an'] = srv['an']
    serverData['server']['sn'] = srv['sn']
    serverData['server']['ctime'] = ds

    for i in range(len(serverData['disk']['raid'])):
        serverData['disk']['raid'][i]['raid_id'] = i
        serverData['disk']['raid'][i]['an'] = srv['an']
        serverData['disk']['raid'][i]['sn'] = srv['sn']
        serverData['disk']['raid'][i]['ctime'] = ds

    for ii in range( len( serverData['disk']['size']) ):
        serverData['disk']['size'][ii]['an'] = srv['an']
        serverData['disk']['size'][ii]['sn'] = srv['sn']
        serverData['disk']['size'][ii]['ctime'] = ds


    r = edb.sys_ipinfos.puts( serverData['ips'] )
    rr = edb.sys_os.puts( [serverData['os']] )
    rrr = edb.sys_servers.puts( [serverData['server']] )
    r4 =  edb.sys_raid.puts( serverData['disk']['raid'] )
    r5 =  edb.sys_disksize.puts( serverData['disk']['size'] )

    if srv['an'] != serverData['an'] or srv['sn'] != serverData['sn']:
        r6 = edb.sys_serverAN.puts( [{'id':'','an':srv['an'],'sn':srv['sn'],'server_an':serverData['an'],'server_sn':serverData['sn'],'ctime':ds}] )

    if r == rr and r == rrr:
        return  r

def compareData( originalData, serverData ):

    result = []
    keys =  serverData.keys()
    for key in keys:
        if key == 'ips':
            for k in serverData[key]:
                for kk in originalData[key]:
                    if k['mac'] == kk['mac'] and k['ipv4'] == kk['ipv4'] and k['ipv6'] == k['ipv6']:
                        pass
                    else:
                        if key not in result:
                            result.append( key )
                        break
        else:
            for k,v in serverData[key].items():
                if originalData[k] != serverData[k]:
                    result.append( key )
    return result

def backupOriginalData( edb , originalData ,srv , part ):


    #TODO must to check diff to back?

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    for k in part:
        if k == 'ips':
            for kk in originalData[k]:
                kk['id'] = ''
                kk['ctime'] = ds
            r = edb.bak_ipinfos.puts( originalData[k] )
        if k == 'os':
            originalData[k]['id'] = ''
            originalData[k]['ctime'] = ds
            r = edb.bak_os.puts( originalData[k] )
        if k == 'server':
            originalData[k]['id'] = ''
            originalData[k]['ctime'] = ds
            r = edb.bak_servers.puts( originalData[k] )
        if k == 'disk':
            for kk in originalData[k]['raid']:
                kk['id'] = ''
                kk['ctime'] = ds

            r = edb.bak_raid.puts( originalData[k] )

            for kk in originalData[k]['size']:
                kk['id'] = ''
                kk['ctime'] = ds
            r = edb.bak_disksize.puts( originalData[k] )

    return r

def updateServerData( edb , serverData , srv ,part ):


    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    for k in part:
        if k == 'ips':
            for kk in serverData[k]:
                #kk['an'] = srv['an']
                #kk['sn'] = srv['sn']
                #kk['id'] = ''
                kk['ctime'] = ds
            r = edb.sys_ipinfos.update( serverData[k] ,where={'an':srv['an'],'sn':srv['sn']} )
        if k == 'os':
            #serverData[k]['an'] = srv['an']
            #serverData[k]['sn'] = srv['sn']
            #serverData[k]['id'] = ''
            serverData[k]['ctime'] = ds
            r = edb.sys_os.update( serverData[k] ,where={'an':srv['an'],'sn':srv['sn']} )
        if k == 'server':
            #serverData[k]['an'] = srv['an']
            #serverData[k]['sn'] = srv['sn']
            #serverData[k]['id'] = ''
            serverData[k]['ctime'] = ds
            r = edb.sys_servers.update( serverData[k] ,where={'an':srv['an'],'sn':srv['sn']} )

        """
        if k == 'raid':
            for i in range(len(serverData[k])):
                serverData[k][i]['raid_id'] = i
                serverData[k][i]['ctime'] = ds


            r = edb.sys_raid.update( serverData[k] ,where={'an':srv['an'],'sn':srv['sn'],'raid_id':serverData[k][]} )
        if k == 'disksize' :
        """


if __name__== '__main__':


    limit = { 'start':0,'offset':100 }

    db = { 'host' : 'localhost',
           'port' : 3306,
           'user' : 'root',
           'passwd' : 'Sina!Puppet!',
           'db' : 'metaDB2',
         }

    edb = easysql.Database( db )

    tunnel = tunnelCore.core()

    while True:

        servers = loadServerBasic( edb ,limit )
#        servers = [
#                    #{ 'an':'05113367','sn':'2VY4V1X','is_collect':'on'},
#                    #{ 'an':'D11080763','sn':'2N1963X','is_collect':'on'}
#
#                        {'an':'D12123142','sn':'65XW4W1','is_collect':'on'},
#                        {'an':'D12123141','sn':'CNR35W1','is_collect':'on'},
#                        {'an':'D12123140','sn':'DNR35W1','is_collect':'on'},
#                        {'an':'D12123139','sn':'8QVY4W1','is_collect':'on'},
#                        {'an':'D12123138','sn':'8WXY4W1','is_collect':'on'},
#                        {'an':'D12123137','sn':'9QVY4W1','is_collect':'on'},
#                        {'an':'D12123136','sn':'5KQ45W1','is_collect':'on'},
#                        {'an':'D12123135','sn':'6KQ45W1','is_collect':'on'},
#                        {'an':'D12123134','sn':'120Y4W1','is_collect':'on'},
#                        {'an':'D12123133','sn':'JGV15W1','is_collect':'on'},
#                        {'an':'D12123132','sn':'9RS45W1','is_collect':'on'},
#                        {'an':'D12123131','sn':'47ZW4W1','is_collect':'on'},
#                        {'an':'D12123130','sn':'BRS45W1','is_collect':'on'},
#                        {'an':'D12123129','sn':'1C3Y4W1','is_collect':'on'},
#                        {'an':'D12123128','sn':'DMW15W1','is_collect':'on'},
#                        {'an':'D12123127','sn':'7YV35W1','is_collect':'on'},
#                        {'an':'D12123126','sn':'8YV35W1','is_collect':'on'},
#                        {'an':'D12123125','sn':'BD0X4W1','is_collect':'on'},
#                        {'an':'D12123124','sn':'850Y4W1','is_collect':'on'},
#                        {'an':'D12123123','sn':'61ZY4W1','is_collect':'on'},
#                        {'an':'D12123122','sn':'BMW15W1','is_collect':'on'},
#                        {'an':'D12123121','sn':'8D0X4W1','is_collect':'on'},
#                        {'an':'D12123120','sn':'584F4W1','is_collect':'on'},
#                        {'an':'D12123119','sn':'B8C45W1','is_collect':'on'},
#                        {'an':'D12123118','sn':'3K625W1','is_collect':'on'},
#                        {'an':'D12123116','sn':'9G6J4X1','is_collect':'on'},
#                        {'an':'D12123114','sn':'HL9X4W1','is_collect':'on'},
#                        {'an':'D12123113','sn':'FC8Z4W1','is_collect':'on'},
#                        {'an':'D12123112','sn':'1Y525W1','is_collect':'on'},
#                        {'an':'D12123111','sn':'4G455W1','is_collect':'on'},
#                        {'an':'D12123110','sn':'JL9X4W1','is_collect':'on'},
#                        {'an':'D12123062','sn':'CLR15W1','is_collect':'on'},
#                        {'an':'D12123061','sn':'96X25W1','is_collect':'on'},
#                        {'an':'D12123060','sn':'2PR15W1','is_collect':'on'},
#                        {'an':'D12123059','sn':'1HZZ4W1','is_collect':'on'},
#                        {'an':'D12123058','sn':'D2VY4W1','is_collect':'on'},
#                        {'an':'D12123057','sn':'H2VY4W1','is_collect':'on'},
#                        {'an':'D12123056','sn':'CDWW4W1','is_collect':'on'},
#                        {'an':'D12123055','sn':'HWP45W1','is_collect':'on'},
#                        {'an':'D12123053','sn':'3RVY4W1','is_collect':'on'},
#                        {'an':'D12123052','sn':'4XQ35W1','is_collect':'on'},
#                        {'an':'D12123051','sn':'4RVY4W1','is_collect':'on'},
#                        {'an':'D12123050','sn':'5XQ35W1','is_collect':'on'},
#                        {'an':'D12123049','sn':'6QR15W1','is_collect':'on'},
#                        {'an':'D12123048','sn':'4C3Y4W1','is_collect':'on'},
#                        {'an':'D12123047','sn':'FMW15W1','is_collect':'on'},
#                        {'an':'D12123046','sn':'9VVY4W1','is_collect':'on'},
#                        {'an':'D12123045','sn':'7QR15W1','is_collect':'on'},
#                        {'an':'D12123044','sn':'GFS15W1','is_collect':'on'},
#                        {'an':'D12123043','sn':'GD0X4W1','is_collect':'on'},
#                        {'an':'D12123042','sn':'2KQ45W1','is_collect':'on'},
#                        {'an':'D12123041','sn':'HKQ45W1','is_collect':'on'},
#                        {'an':'D12123040','sn':'HMW15W1','is_collect':'on'},
#                        {'an':'D12123039','sn':'CYT45W1','is_collect':'on'},
#                        {'an':'D12123038','sn':'2C3Y4W1','is_collect':'on'},
#                        {'an':'D12123037','sn':'JFS15W1','is_collect':'on'},
#                        {'an':'D12123036','sn':'2PQ45W1','is_collect':'on'},
#                        {'an':'D12123035','sn':'HNR35W1','is_collect':'on'},
#                        {'an':'D12123034','sn':'7RVY4W1','is_collect':'on'},
#                        {'an':'D12123033','sn':'DKR35W1','is_collect':'on'},
#                        {'an':'D12123032','sn':'4SVY4W1','is_collect':'on'},
#                        {'an':'D12123031','sn':'G50Y4W1','is_collect':'on'},
#                        {'an':'D12123030','sn':'72XW4W1','is_collect':'on'},
#                        {'an':'D12123029','sn':'B20Y4W1','is_collect':'on'},
#                        {'an':'D12123028','sn':'CCS15W1','is_collect':'on'},
#                        {'an':'D12123027','sn':'CKR35W1','is_collect':'on'},
#                        {'an':'D12123026','sn':'C1XW4W1','is_collect':'on'},
#                        {'an':'D12123025','sn':'1MQ45W1','is_collect':'on'},
#                        {'an':'D12123024','sn':'22XW4W1','is_collect':'on'},
#                        {'an':'D12123023','sn':'BLR35W1','is_collect':'on'},
#                        {'an':'D12123022','sn':'C1ZY4W1','is_collect':'on'},
#                        {'an':'D12123021','sn':'91XW4W1','is_collect':'on'},
#                        {'an':'D12123020','sn':'7D0X4W1','is_collect':'on'},
#                        {'an':'D12123019','sn':'H10Y4W1','is_collect':'on'},
#                        {'an':'D12123018','sn':'B30Y4W1','is_collect':'on'},
#                        {'an':'D12123017','sn':'HJR35W1','is_collect':'on'},
#                        {'an':'D12123016','sn':'HCS15W1','is_collect':'on'},
#                        {'an':'D12123015','sn':'8SVY4W1','is_collect':'on'},
#                        {'an':'D12123014','sn':'5RVY4W1','is_collect':'on'},
#                        {'an':'D12123013','sn':'GCS15W1','is_collect':'on'},
#                        {'an':'D12122012','sn':'FG9G4W1','is_collect':'on'},
#                        {'an':'D12122011','sn':'9R7K4W1','is_collect':'on'},
#                        {'an':'D12122010','sn':'1G9G4W1','is_collect':'on'},
#                        {'an':'D12122009','sn':'6T2C4W1','is_collect':'on'},
#                        {'an':'D12122007','sn':'204F4W1','is_collect':'on'},
#                        {'an':'D12122006','sn':'8YDH4W1','is_collect':'on'},
#                        {'an':'D12122004','sn':'77FL4W1','is_collect':'on'},
#                        {'an':'D12122003','sn':'63HD4W1','is_collect':'on'},
#                        {'an':'D12122002','sn':'CYDH4W1','is_collect':'on'},
#                        {'an':'D12122001','sn':'43HD4W1','is_collect':'on'},
#                        {'an':'D12121989','sn':'85D35W1','is_collect':'on'},
#                        {'an':'D12121988','sn':'C3KW4W1','is_collect':'on'},
#                        {'an':'D12121987','sn':'7FF15W1','is_collect':'on'},
#                        {'an':'D12121986','sn':'8SHY4W1','is_collect':'on'},
#                        {'an':'D12121985','sn':'8FNX4W1','is_collect':'on'},
#                        {'an':'D12121984','sn':'7SHY4W1','is_collect':'on'},
#                        {'an':'D12121976','sn':'5SHY4W1','is_collect':'on'},
#                        {'an':'D12121975','sn':'5FF15W1','is_collect':'on'},
#                        {'an':'D12121974','sn':'3FNX4W1','is_collect':'on'},
#                        {'an':'D12121934','sn':'B3KW4W1','is_collect':'on'}
#
#
#                  ]

        for srv in servers:
            s = loadServerTunnelIP( edb , srv['an'] )
            if len( s )  != 0:
                srv['tunnel_ip'] =  s[0]['tunnel_ip']
            else:
                srv['tunnel_ip'] = ''

            if srv['is_collect'] == 'on' and srv['tunnel_ip'] != '':

                originalData = loadOriginalData( edb , srv)

                if len(originalData) == 0:
                    try:
                        serverData = getServerData( tunnel , srv , 'reload')
                        storeServerInfo( edb , serverData , srv )
                    except KeyboardInterrupt:
                        print 'user cancel'
                        break
                    except:
                        print 'server %s is not add meta client code!' % srv['an']
                else:
                    try:
                        serverData = eval(getServerData( tunnel , srv , 'reload'))
                        if serverData == None:
                            pass
                        else:
                            part = compareData( originalData , serverData )
                            if len(part) !=  0 :
                                backupOriginalData( edb, originalData ,srv ,part )
                                updateServerData( edb, serverData ,srv ,part )
                    except:
                        print 'server %s  meta client code error!' % srv['an']
            else:
                print srv['an'] + ' was not tunnel_ip added.'

        limit['start'] += limit['offset']
        #if limit['start'] == 100:
        #    break
        if len( servers ) < limit['offset']:
            break



