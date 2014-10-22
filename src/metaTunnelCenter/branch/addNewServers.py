import pprint
import types
from lib import easysql
from lib import tunnelCore

def getNewServers( edb ):

    r = edb.new_server_checks.gets( all , where={ 'state':'new' } )
    return r

def isCollector( srv ,edb ):

    r = edb.sys_os.gets( all , where={ 'an': srv['asset_number'] } )
    if len(r) != 0 :
        srv['state'] = 'finish'
        edb.new_server_checks.update( [srv] , where={ 'asset_number': srv['asset_number'] } )
        return True
    else:
        return False


def getServerData( tunnel ,srv ,action):

    res = tunnel.get( srv , 'sudo python /usr/local/meta/metaCollecter.py '+ action )

    if type( res ) == types.UnicodeType:
        try:
            return eval( res )
        except:
            return {'err':res}
    else:
        return res



if __name__ == '__main__':


    db = { 'host' : '10.210.231.41',
           'port' : 3306,
           'user' : 'micragent',
           'passwd' : 'sina.com',
           'db' : 'metaDB4',
         }

    edb = easysql.Database( db )


    tunnel = tunnelCore.core( {'method':'async' } )



    servers = getNewServers( edb )
    print len( servers )
    for serv in servers:
        if isCollector( serv ,edb ):
            print serv['asset_number'] +'is add in db.'
        else:
            print serv
            serverData = getServerData( tunnel , [serv['ip']], 'reload' )
            pprint.pprint( serverData )

