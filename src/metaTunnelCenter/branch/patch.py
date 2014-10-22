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
    elif err == 'cmdb':
        logging.error('Server an :'+ server  + ' ip not in CMDB...' )
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




def loadOriginalData( edb ,srv ):

    d = {}
    ips = edb.sys_ipinfos.gets( all , where={'an':srv['an'] } )
    osInfo = edb.sys_os.gets( all , where={'an':srv['an'] } )
    srvInfo = edb.sys_servers.gets( all , where={'an':srv['an'] } )
    raidInfo = edb.sys_raid.gets( all , where={'an':srv['an'] } )
    disksize = edb.sys_disksize.gets( all , where={'an':srv['an'] } )
    physical_disk = edb.sys_physical_disk.gets( all , where={'an':srv['an']} )


    if len(ips) != 0:
        d['ips'] = ips
    else:
        d['ips'] = []

    if  len(osInfo) != 0:
        d['os'] = osInfo[0]
    else:
        d['os'] = {}

    if len(srvInfo) != 0:
        d['server'] = srvInfo[0]
    else:
        d['server'] = {}

    if len( raidInfo )  != 0:
        d['raid'] = raidInfo
    else:
        d['raid'] = []

    if len( disksize ) !=0:
        d['disksize'] = disksize
    else:
        d['disksize'] = []

    if len( physical_disk ) !=0:
        d['physical_disk'] = physical_disk
    else:
        d['physical_disk'] = []


    if  len(d['ips']) == 0 and len(d['os']) == 0 and len(d['server']) == 0 and len(d['raid']) == 0 and len(d['disksize']) == 0 and len(d['physical_disk']) == 0 :
        return {}
    else:
        return d


def getServerData( tunnel ,srv ,action):

    res = tunnel.get( srv , 'sudo python /usr/local/meta/metaCollecter.py '+ action )

    if type( res ) == types.UnicodeType:
        try:
            return eval( res )
        except:
            return {'err':res}
    else:
        return res

def storeServerInfo( edb , serverData , srv ):


    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    #serverData =  eval(serverData)

    pprint.pprint( serverData )

    if serverData.has_key('sn'):
        if serverData['sn'] == None:
            serverData['sn'] = 'undefined'
    else:
        serverData['sn'] = 'undefined'

    #ips = serverData['ips']
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

                    if len(serverData['disk']['pdisk'][iii]['size']) > 10 :
                        serverData['disk']['pdisk'][iii]['size'] = serverData['disk']['pdisk'][iii]['size'][0:10]

                    if len(serverData['disk']['pdisk'][iii]['interface']) >  20 :
                        serverData['disk']['pdisk'][iii]['interface'] = serverData['disk']['pdisk'][iii]['interface'][0:20]

                    serverData['disk']['pdisk'][iii]['an'] = srv['an']
                    serverData['disk']['pdisk'][iii]['sn'] = serverData['sn']
                    serverData['disk']['pdisk'][iii]['ctime'] = ds

                r6 =  edb.sys_physical_disk.puts( serverData['disk']['pdisk'] )



    if len(serverData['os']['os_version'] ) > 5 :
        serverData['os']['os_version'] = serverData['os']['os_version'][0:5]


    rr = edb.sys_os.puts( [serverData['os']] )
    rrr = edb.sys_servers.puts( [serverData['server']] )




        # save  route , dns and sudoers info 
    if serverData.has_key( 'route' ):

        if serverData['route'].has_key('dns'):
            if len( serverData['route']['dns'] ) != 0:
                for dns in range( len( serverData['route']['dns'] ) ):
                    serverData['route']['dns'][dns]['an'] = srv['an']
                    serverData['route']['dns'][dns]['sn'] = serverData['sn']
                    serverData['route']['dns'][dns]['ctime'] = ds

                edb.sys_dns.puts( serverData['route']['dns'] )

        if serverData['route'].has_key('route'):
            if len( serverData['route']['route'] ) != 0:
                for route in range( len( serverData['route']['route'] ) ):
                    serverData['route']['route'][route]['an'] = srv['an']
                    serverData['route']['route'][route]['sn'] = serverData['sn']
                    serverData['route']['route'][route]['ctime'] = ds

                edb.sys_route.puts( serverData['route']['route'] )

        if serverData['route'].has_key('sudoers'):
            if len( serverData['route']['sudoers'] ) != 0:
                for sudo in range( len( serverData['route']['sudoers'] ) ):
                    if len(serverData['route']['sudoers'][sudo]['passwd'] ) > 50 :
                        serverData['route']['sudoers'][sudo]['passwd'] = serverData['route']['sudoers'][sudo]['passwd'][0:50]

                    serverData['route']['sudoers'][sudo]['an'] = srv['an']
                    serverData['route']['sudoers'][sudo]['sn'] = serverData['sn']
                    serverData['route']['sudoers'][sudo]['ctime'] = ds

                edb.sys_sudoers.puts( serverData['route']['sudoers'] )


    if serverData.has_key( 'an' ):
        if srv['an'] != serverData['an'] :
            r6 = edb.sys_serverAN.puts( [{'an':srv['an'],'sn':serverData['sn'],'server_an':serverData['an'],'server_sn':serverData['sn'],'ctime':ds}] )
    else:
            r6 = edb.sys_serverAN.puts( [{'an':srv['an'],'sn':serverData['sn'],'server_an':srv['an'],'server_sn':serverData['sn'],'ctime':ds}] )


def compareData( originalData, serverData ):


    #pprint.pprint( originalData )
    #pprint.pprint( serverData )

    result = {}

    #keys =  serverData.keys()
    #for key in keys:
    if True:
        #if key == 'ips':
        if serverData.has_key( 'ips' ):
            if len(originalData['ips']) == 0:
                result['ips'] = serverData['ips']
            else:
                result['ips'] = []

                for k in serverData['ips']:
                    k_status = False
                    for kk in originalData['ips']:
                        if k['mac'] == kk['mac'] and k['ipv4'] == kk['ipv4'] and k['ipv6'] == k['ipv6']:
                            k_status = True

                    if k_status == True:
                        pass
                    else:
                        result['ips'].append( k )
        else:
            result['ips'] = []


        if  serverData.has_key('disk'):
            if len(originalData['disksize'] ) == 0 :
                if serverData['disk'].has_key( 'size' ) and serverData['disk']['size'] != None:
                    result['disksize'] =  serverData['disk']['size']
                else:
                    result['disksize'] = []
            else:
                result['disksize'] = []
                for k in serverData['disk']['size']:
                    k_status = False
                    for kk in originalData['disksize']:
                        if k['point'] == kk['point'] and k['size'] == kk['size']:
                            k_status = True
                    if k_status == True:
                        pass
                    else:
                        result['disksize'].append( k )


            if len( originalData['raid'] ) == 0:
                if serverData['disk'].has_key( 'raid' ):
                    result['raid'] = serverData['disk']['raid']
                else:
                    result['raid'] = []
            else:
                result['raid'] = []
                for k in serverData['disk']['raid']:
                    k_status = False
                    for kk in originalData['raid']:
                        if k['level'] == kk['level']:
                            k_status = True
                    if k_status == True:
                        pass
                    else:
                        result['raid'].append( k )

            if len( originalData['physical_disk'] ) == 0:
                if serverData['disk'].has_key( 'pdisk' ):
                    result['physical_disk'] = serverData['disk']['pdisk']
                else:
                    result['physical_disk'] = []
            else:
                result['physical_disk'] = []
                for k in serverData['disk']['pdisk']:
                    k_status = False
                    for kk in originalData['physical_disk']:
                        if k['slot'] == kk['slot'] and k['size'] == kk['size'] and k['interface'] == kk['interface'] :
                            k_status = True

                    if k_status == True:
                        pass
                    else:
                        result['physical_disk'].append( k )
        else:
            result['disksize'] = []
            result['raid'] = []
            result['physical_disk'] = []


        if serverData.has_key( 'server' ):
            result['server'] = {}
            for k,v in serverData['server'].items():
                if originalData['server'].has_key( k ):
                    if  str(serverData['server'][k]) != str(originalData['server'][k]):
                        result['server'] = serverData['server']
                        break
                else:
                    result['server'] = serverData['server']

        else:
            result['server'] = {}


        if serverData.has_key( 'os' ):
            result['os'] = {}
            for k,v in serverData['os'].items():
                if originalData['os'].has_key( k ):
                    if  str(serverData['os'][k]) != str(originalData['os'][k]):
                        result['os'] = serverData['os']
                        break
                else:
                    result['os'] = serverData['os']
        else:
            result['os'] = {}



    #pprint.pprint( serverData )
    #pprint.pprint( result )

    if len( result['disksize'] ) == 0:
        result.pop( 'disksize' )
    if len( result['raid'] ) == 0:
        result.pop( 'raid' )
    if len( result['ips'] ) == 0:
        result.pop( 'ips' )
    if len(result['physical_disk'] ) ==0:
        result.pop( 'physical_disk' )
    if len( result['server'] ) ==0:
        result.pop( 'server' )
    if len( result['os'] ) == 0:
        result.pop( 'os' )


    if len( result ) != 0:
        result['an'] = originalData['os']['an']
        if serverData.has_key( 'sn' ):
            result['sn']  = serverData['sn']
        else:
            result['sn'] = originalData['os']['sn']


    return result

def backupOriginalData( edb , originalData  ):


    #TODO must to check diff to back?

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')


    if originalData.has_key( 'ips' ):
        for i in range(len(originalData['ips'])):
            originalData['ips'][i]['id'] = ''
            originalData['ips'][i]['ctime'] = ds

        r = edb.chg_ipinfos.puts( originalData['ips'] )

    if originalData.has_key( 'disksize'):
        for i in range(len(originalData['disksize'])):
            originalData['disksize'][i]['id'] = ''
            originalData['disksize'][i]['ctime'] = ds
        r5 =  edb.chg_disksize.puts( originalData['disksize'] )

    if originalData.has_key( 'physical_disk' ):
        for i in range(len(originalData['physical_disk'])):
            originalData['physical_disk'][i]['id'] = ''
            originalData['physical_disk'][i]['ctime'] = ds
        r6 =  edb.chg_physical_disk.puts( originalData['physical_disk'] )

    if originalData.has_key( 'raid' ):
        for i in range(len(originalData['raid'])):
            originalData['raid'][i]['id'] = ''
            originalData['raid'][i]['ctime'] = ds

        r4 =  edb.chg_raid.puts( originalData['raid'] )


    if originalData.has_key('server') :
        originalData['server']['id'] = ''
        originalData['server']['ctime'] = ''

        rrr = edb.chg_servers.puts( [originalData['server']] )

    if originalData.has_key( 'os' ):
        originalData['os']['id'] = ''
        originalData['os']['ctime'] = ''
        rr = edb.chg_os.puts( [originalData['os']] )



def updateServerData( edb , serverData  ):


    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')


    #pprint.pprint( serverData )

    for k in serverData.keys():

        if k == 'os':
            serverData[k]['an'] = serverData['an']
            serverData[k]['sn'] = serverData['sn']
            serverData[k]['ctime'] = ds

            r = edb.sys_os.update( [serverData[k]] ,where={'an':serverData['an']} )

        if k == 'server':
            serverData[k]['an'] = serverData['an']
            serverData[k]['sn'] = serverData['sn']
            serverData[k]['ctime'] = ds

            r = edb.sys_servers.update( [serverData[k]] ,where={'an':serverData['an']} )

        if k == 'ips':
            for kk in serverData[k]:
                kk['an'] = serverData['an']
                kk['sn'] = serverData['sn']
                kk['ctime'] = ds
                try:
                    r = edb.sys_ipinfos.update( [kk] ,where={'an':kk['an'] , 'mac':kk['mac'] } )
                except:
                    r = edb.sys_ipinfos.puts( [kk] )

        if k == 'disk':
            for i in range(len(serverData[k]['raid'])):
                serverData[k]['raid'][i]['raid_id'] = i
                serverData[k]['raid'][i]['ctime'] = ds
                serverData[k]['raid'][i]['an'] = serverData['an']
                serverData[k]['raid'][i]['sn'] = serverData['sn']

                try:
                    r = edb.sys_raid.update( [ serverData[k]['raid'][i] ] , where={'an':serverData['an'],'raid_id':serverData[k]['raid'][i]['raid_id'] } )
                except:
                    r = edb.sys_raid.puts( [serverData[k]['raid'][i]]  )

            for i in range( len( serverData[k]['disksize'] ) ):
                serverData[k]['disksize'][i]['ctime'] = ds
                serverData[k]['disksize'][i]['an'] = serverData['an']
                serverData[k]['disksize'][i]['sn'] = serverData['sn']
                serverData[k]['disksize'][i]['id'] = ''

                try:
                    r = edb.sys_raid.update( serverData[k][i] ,where={'an':serverData['an'],'point':serverData[k]['disksize'][i]['point'] } )
                except:
                    r = edb.sys_raid.puts( [serverData[k]['disksize'][i]] )

            for i in range( len( serverData[k]['physical_disk'] ) ):
                serverData[k]['physical_disk'][i]['ctime'] = ds
                serverData[k]['physical_disk'][i]['an'] = serverData['an']
                serverData[k]['physical_disk'][i]['sn'] = serverData['sn']
                serverData[k]['physical_disk'][i]['id'] = ''

                try:
                    r = edb.sys_raid.update( serverData[k][i] , where={'an':serverData['an'],'slot':serverData[k]['physical_disk'][i]['slot'] } )
                except:
                    r = edb.sys_raid.puts( [serverData[k]['physical_disk'][i]] )


    #pprint.pprint( serverData )


def main( name , servers , tunnel):


    db = { 'host' : '10.210.66.81',
           'port' : 3306,
           'user' : 'micragent',
           'passwd' : 'sina.com',
           'db' : 'metaDB',
         }

    edb = easysql.Database( db )



    for srv in servers:

        try:
            if len(srv['ips']) > 1:

                for ip in srv['ips'] :
                    for i in range(3):
                        serverData = getServerData( tunnel , [ip] , 'reload')
                        if serverData == None or serverData == 'None' or serverData.has_key('err'):
                            pass
                        else:
                            break
                    try:
                        if serverData['err'] != '':
                            pass
                    except:
                        break
            elif len( srv['ips'] ) == 0:
                serverData = 'NoIP'
            else:
                ip = srv['ips']
                for i in range( 3 ):
                    serverData = getServerData( tunnel , ip , 'reload')
                    if serverData == None or serverData == 'None' or serverData.has_key('err'):
                        pass
                    else:
                        break


            if type( serverData ) in (types.DictType ,types.NoneType):
                if serverData == None:
                    errorlog( srv , {'err':None,'data':serverData} )
                elif serverData.has_key('err'):
                    errorlog( srv , serverData )
                elif serverData == '' or serverData == 'None':
                    errorlog( srv , '' )
                elif serverData == 'NoIP':
                    errorlog( srv , 'NoIP' )
                else:
                    originalData = loadOriginalData( edb , srv )

                    try:
                        #serverData =  eval(serverData)
                        print srv
                        if len(originalData) == 0 :
                            #pprint.pprint( serverData )
                            storeServerInfo( edb , serverData , srv )
                            print 'store data '
                            errorlog( srv , 'ok' )

                        else:
                            if serverData == None:
                                print 'no data update'
                            else:
                                part = compareData( originalData , serverData )
                                if len(part) !=  0 :
                                    print 'update data'
                                    backupOriginalData( edb, originalData )
                                    updateServerData( edb, part  )
                                else:
                                    print 'No Changed.'

                    except SyntaxError:
                        errorlog( srv, {'err':'other','data':serverData} )


            elif type( serverData ) == types.UnicodeType:
                errorlog( srv , {'err':'unknown','data':serverData} )

        except KeyboardInterrupt:

            print 'user cancel'
            break




if __name__== '__main__':


    tunnel = tunnelCore.core( {'method':'async' } )

    servers = []

    with open( 'servers2.txt', 'r' ) as fp:
        lines = fp.readlines()
        for line in lines:
            an,ips = line.split('\t')
            if len( ips ) > 10 :
                ip = ips.split(';')
                tunnel_ip = []
                for i in ip:
                    if i != '\n':
                        if i.startswith( '外网' ):
                            tunnel_ip.append(i.split('-')[1].strip())
                        elif i.startswith( '内网' ):
                            tunnel_ip.append( i.split('-')[1].strip())
                d = { 'an': an , 'ips': tunnel_ip }
                servers.append( d );
            else:
                errorlog( an , 'cmdb' )

    maxThread = 100
    minThread = 1

    total_server = len( servers )


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

#    pprint.pprint( len(rr) )
#    print len( rr )
#    for  ii in range( maxThread ):

    for  ii in range( len(rr) ):
        t= threading.Thread( target=main, args=(ii,rr[ii],tunnel ) )
        t.start()

#    for srv in servers:
#        print srv
#    main('start', rr[42] , tunnel )


