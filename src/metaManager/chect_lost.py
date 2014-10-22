import pprint
from conf import dbinfo
from modules import easysql

def readsite( filename ) :

    an = []
    fp = open ( filename , 'r')  
    lines = fp.readlines()
    for line in lines:
        r = line.split( '\t')
        #an.append( r[0] )
        an.append( r )

    return an


def readLost( filename ):

    an = []
    fp = open ( filename , 'r')  
    lines = fp.readlines()
    for line in lines:
        r = line.split( '\n')
        an.append( r[0] )
        #an.append( r )

    return an



def check(edb , an ):



    r = edb.sys_times.gets( all , where={ 'an': an } )


    if len( r ) > 0 :
        return True
    else:
        return False


if __name__ == '__main__':


    r = []
    edb = easysql.Database( dbinfo.dbs['infodb']['r'] )

    servers = readsite( 'servers/site-servers.txt' )
    losts = readLost( 'lost.yf' )
    for x in losts:
        if not check( edb , x ) :
            #print x[0] , x[1] , x[2] , x[3]
            print x
            #r.append( x )
            for xx in servers :
                if x == xx[0]:
                    r.append(xx[3].split('\n')[0])

    #print r
