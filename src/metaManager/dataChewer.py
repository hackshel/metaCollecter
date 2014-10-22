# -*- coding: utf-8 -*-

import os
import time
import os.path
import pprint
import datetime
import logging
from conf import dbinfo
from modules import easysql

from modules import daemonize
from modules import genlog
from modules import defines



#def readLocalRc( edb , startId ) :
def readLocalRc( edb  ) :
    #r = edb.sys_times.gets( all , where={'id':(startId, '')}, limit=100)
    r = edb.sys_times.gets( all , where={'sync_state':'no-sync' }, limit=100 )
    return r

def readCenterRc( edb, an ):
    r = edb.sys_times.gets( all ,where={'an': an })
    return r

def writeTimsData( edb , localTimes ):

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    #print localTimes
    if len(localTimes) != 0:
        localTimes.pop('id')
        localTimes['ctime'] = ds
        localTimes['rsync_state'] = 'no-update'
        localTimes['state'] = 'curr'


    r = edb.sys_times.puts( [ localTimes] )

    if r :
        res = edb.sys_times.gets( all , where= {'an':localTimes['an'], 'md5' : localTimes['md5'], 'rsync_state' : 'no-update' } )
    else:
        res = ''

    return res[0]['id']

def writeServerData( edb , localData ,times_id ) :

    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')


    if localData.has_key( 'os' ):

        localData['os'][0].pop( 'id' )
        localData['os'][0]['ctime'] = ds
        localData['os'][0]['times_id'] = times_id

        edb.sys_os.puts( localData['os'] )

    if localData.has_key( 'disksize' ):
        for x in localData['disksize']:
            x.pop( 'id' )
            x['ctime'] = ds
            x['times_id'] = times_id

        edb.sys_disksize.puts( localData['disksize'] )

    if localData.has_key( 'dns' ):
        for x in localData['dns']:
            x.pop( 'id' )
            x['ctime'] = ds
            x['times_id'] = times_id

        edb.sys_dns.puts( localData['dns'] )

    if localData.has_key( 'ipinfos' ):
        for x in localData['ipinfos']:
            x.pop( 'id' )
            x['ctime'] = ds
            x['times_id'] = times_id

        edb.sys_ipinfos.puts( localData['ipinfos'] )

    if localData.has_key( 'pdisk' ):
        for x in localData['pdisk']:
            x.pop( 'id' )
            x['ctime'] = ds
            x['times_id'] = times_id

        edb.sys_physical_disk.puts( localData['pdisk'] )

    if localData.has_key( 'raid' ):
        for x in localData['raid']:
            x.pop( 'id' )
            x['ctime'] = ds
            x['times_id'] = times_id

        edb.sys_raid.puts( localData['raid'] )

    if localData.has_key( 'route' ):
        for x in localData['route']:
            x.pop( 'id' )
            x['ctime'] = ds
            x['times_id'] = times_id

        edb.sys_route.puts( localData['route'] )

    if localData.has_key( 'servers' ):

        localData['servers'][0].pop( 'id' )
        localData['servers'][0]['ctime'] = ds
        localData['servers'][0]['times_id'] = times_id

        edb.sys_servers.puts( localData['servers'] )

    if localData.has_key( 'sudoers' ):
        for x in localData['sudoers']:
            x.pop( 'id' )
            x['ctime'] = ds
            x['times_id'] = times_id

        edb.sys_sudoers.puts( localData['sudoers'] )


def getServerData( edb , localRC ):
    sys_os = edb.sys_os.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )
    sys_disksize = edb.sys_disksize.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )
    sys_dns = edb.sys_dns.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )
    sys_ipinfos = edb.sys_ipinfos.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )
    sys_pdisk = edb.sys_physical_disk.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )
    sys_raid = edb.sys_raid.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )
    sys_route = edb.sys_route.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )
    sys_servers = edb.sys_servers.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )
    sys_sudoers = edb.sys_sudoers.gets( all , where={ 'an':localRC['an'] , 'times_id': localRC['id'] } )

    rs = {}
    rs['os'] =  sys_os
    rs['disksize'] = sys_disksize
    rs['dns']  = sys_dns
    rs['ipinfos'] = sys_ipinfos
    rs['pdisk'] =  sys_pdisk
    rs['raid'] = sys_raid
    rs['route']  = sys_route
    rs['servers'] = sys_servers
    rs['sudoers'] = sys_sudoers
    rs['times'] = localRC

    return rs


def changeCenterRcState( edb , centerData ):
    up_rc = edb.sys_times.update( [{'state':'chg','rsync_state':'invalid'}] , where={ 'an': centerData['an'], 'md5':centerData['md5']})
    return up_rc

def writeIdFile( filename , lastId ):

    try:
        with open( filename ,'w' ) as fp:
            fp.write( lastId )
            fp.close()

        return True
    except:
        return False


def readIDFile( filename ):

    ids = ''

    if os.path.exists( filename ):

        with open ( filename ,'r' ) as fp:
            lines = fp.readlines()
            for line in lines:
                r = line.split('\n')
                if r[0] == '':
                    ids = '0'
                else:
                    ids =  r[0]
            fp.close()

    else:

        with open ( filename ,'w') as fp:
            fp.write('0')
            fp.close()

        ids = 0

    return ids

def updateLocalSyncState( edb , local ):


    r = edb.sys_times.update( [{'sync_state':'synced' , 'state':'curr'}] , where={ 'an':local['an'] , 'md5':local['md5'] })

    return r


if __name__ == '__main__':

    def main():
        path = './conf/chew.id'

        localDB  = easysql.Database( dbinfo.dbs['infodb']['r'] )
        centerDB = easysql.Database( dbinfo.dbs['infodb']['w'] )

        while True:
            #ids = readIDFile( path )
            #localRC = readLocalRc( localDB , ids )
            localRC = readLocalRc( localDB  )
            if len( localRC ) == 0:
                lastId = 0
            else:
                lastId = localRC[-1]['id']

            for local in localRC:

                rx = localDB.sys_times.update( [{'state':'chg'}] , where={ 'an':local['an'] } )

                centerRC = readCenterRc( centerDB , local['an'] )
                if len( centerRC ) != 0:
                    state = False
                    for center in centerRC:

                        if center['state'] == 'curr':
                            if center['an'] == local['an'] and center['md5'] == local['md5']:
                                if local['sync_state'] == 'no-sync': #re-sync
                                    updateLocalSyncState( localDB , local )
                                    break
                            else:
                                print changeCenterRcState( centerDB ,  center )
                                localData = getServerData( localDB , local )
                                times_id = writeTimsData( centerDB , local )
                                if times_id != '':
                                    writeServerData( centerDB , localData , times_id )
                                updateLocalSyncState( localDB , local )

                        #if center['an'] == local['an'] and center['md5'] == local['md5']:
                        #    if center['state'] == 'curr':
                        #        if local['sync_state'] == 'no-sync': #re-sync
                        #            updateLocalSyncState( localDB , local )
                        #            break
                        #    else:
                        #        print 'update curr to chg'

                        #else:
                        #    if center['state'] == 'chg':
                        #        pass
                        #    elif center['state'] == 'curr':
                        #        print 'update center curr data to back'
                        #        localData = getServerData( localDB , local )
                        #        print changeCenterRcState( centerDB ,  center )
                        #        times_id = writeTimsData( centerDB , local )
                        #        if times_id != '':
                        #            writeServerData( centerDB , localData , times_id )
                        #        updateLocalSyncState( localDB , local )

                else:
                    print 'insert server ' + local['an']
                    localData = getServerData( localDB , local )
                    times_id = writeTimsData( centerDB , local )
                    if times_id != '':
                        writeServerData( centerDB , localData , times_id )

                    updateLocalSyncState( localDB , local )

            #print 'last id is ' + str(lastId) , writeIdFile( path , str(lastId) )
            print 'last id is ' + str( lastId )
            time.sleep( 60 )

    logger = genlog.logger
    dumbLogger = logging.Logger( '_dumb_' )
    dumbLogger.setLevel( logging.CRITICAL )


    PID_PATH = defines.PIDPATH['managerChewer']

    daemonize.standard_daemonize( main, PID_PATH)
 
