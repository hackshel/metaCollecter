# -*- coding: utf-8 -*-
from modules import tunnelCore
import httplib
import pprint
import logging
import datetime
import os
import json


def errorlog( error ):

    dt = datetime.datetime.now()

    ds = dt.strftime('%Y%m%d%H%M%S')

    logPath = '/'

    logfile = 'server' + ds + '.log'

    logging.basicConfig( filename = os.path.join(os.getcwd()+logPath, logfile),
                         level = logging.WARN,
                         filemode = 'w',
                         format = '%(asctime)s - %(levelname)s: %(message)s'
                        )

    logging.error( error )



def readErrorAn( filename ):

    ans = []

    with open( filename , 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            #ans.append( line.split('\n')[0].strip() )
            an,sn = line.split()
            ans.append({'an':an,'sn':sn})
        fp.close()

    return ans

def readServers( filename ):

    res = []

    with open( filename , 'r' ) as fp:
        lines = fp.readlines()
        for line in lines:
            d = {}
            an , ip =  line.split()
            d['an'] = an.strip()
            d['ip'] = ip.split('\n')[0].strip()
            res.append( d )

        fp.close()

    return  res


def getServerData( tunnel ,srv ,action):

    res = tunnel.get( srv , 'sudo python /usr/local/meta/metaCollecter.py '+ action )

    return res


def linkQuery( sip ):

    host = '10.13.8.60'
    port = 5666
    url  = '/link_query'

    headers =  {   "Content-type": "application/json",
                        "Accept": "text/plain"
                    }


    query_type == 'serv_ip'

    conn = httplib.HTTPConnection( host , port  , timeout=10 )
    params = json.dumps({'type': query_type , 'sip': ip })

    conn.request( 'POST' ,url, params ,headers )


    res = conn.getresponse()

    if res.status == 200:
        ret = eval(res.read())
        if ret['code'] == 0 :
            msg = eval( ret['msg'])
            if len( msg ) != 0:
                for fm in msg:
                    result['link'].append( fm )

    return result



def check_error( result , errors ,ips ):
    res = []
    for i in range(len(result)) :
        tmp = []
        try:
            r = eval( result[i] )
        except:
            r = result[i]

        try:
            if r.has_key('err'):
                errorlog( 'return error ' + json.dumps( r ) +' #'+ str(ips[i]) )
            else:
                if r['sn'] == None:
                    errorlog( 'no an or sn ' +' #'+ str(ips[i]) )
                elif r['sn'].startswith('NC'):
                    for err in errors:
                        if r['sn'].lower() == err['sn'].lower():
                            tmp['ips'] = r['ips']
                            tmp['an'] = r['an']
                            tmp['sn'] = r['an']
                            res.append( tmp )
                            #pprint.pprint( r )
                        #break

        except:
            errorlog( 'not std error ' + json.dumps(r) +' #' + str(i) + ' #' + str(ips[i]) )


    return res


def printlnServer( result ):
    for i in range(len(result)) :
        try:
            r = eval( result[i] )
        except:
            r = result[i]



        try:
            if r.has_key('err'):
                errorlog( 'return error ' + json.dumps( r ) +' #'+ str(ips[i]) )
            else:
                if r['sn'] == None:
                    errorlog( 'no an or sn ' +' #'+ str(ips[i]) )
                else:
                    #print r['an']+"\t"+ r['sn']+"\t"+r['ips']+"\n"
                    ipss = []
                    for x in r['ips']:
                        ipss.append( x['ipv4'] )

                    s = ','.join( ipss )

                    print r['an']+"\t"+r['sn']+"\t"+s

        except:
            errorlog( 'not std error ' + json.dumps(r) +' #' + str(i) + ' #' + str(ips[i]) )







if __name__ == '__main__':


    error_an = './servers/error-an.txt'

    servers = './servers/result.txt'

    errors =  readErrorAn( error_an )

    maxLen = 100

    tunnel = tunnelCore.core( {'method':'async' } )


    libs = readServers( servers )

    rr  = []

    total_server = len( libs )

    MaxTimes = total_server / maxLen

    if total_server % maxLen > 0:
        MaxTimes += 1

    print MaxTimes

    for i in range( MaxTimes ):
        rr.append( libs[maxLen*i:maxLen*(i+1)] )


    for r in rr:
        ips = []
        for x in r:
            ips.append( x['ip'] )

        result = getServerData( tunnel , ips , 'reload' )
        printlnServer( result )
        #print result
        #err = check_error( result , errors ,ips)
        #if len( err ) !=0:
        #    pprint.pprint( err )
        #break




    """
    import pprint
    for err in errors:
        for lib in libs:
            if err == lib['an']:
                #res.append( lib )
                #res.append( lib['an'] )
                if lib['an'] not in res:
                    res.append( lib['an'] )
                    ips.append( lib )
                    #errors.remove( err )
                #if err in errors:
                #    errors.remove( err )


    #pprint.pprint (res)
    #print len(ips)

    for r in res:
        if r in errors:
            errors.remove( r )


    print ','.join(errors)


    for x in ips:

        result = getServerData( tunnel , [ x['ip'] ] , 'reload' )
        try:
            xo = eval( result[0] )
        except:
            xo = result[0]

        #link = linkQuery( x['ip'] )

        try:
            ir = []
            for rr in xo['ips']:
                ir.append( rr['ipv4'] )
            print x['an']+',' , xo['an'] +',', xo['sn']+',' , ';'.join( ir )

        except:
            print x['an']+',' ,result

    """



    """
    result = getServerData( tunnel , ips , 'reload' )

    #pprint.pprint( result )
    for x in result :
        try:
            xo = eval( x )
            ips = []
            for ip in xo['ips']:
                ips.append( ip['ipv4'] )
            print xo['an'] , xo['sn'] , ','.join( ips )
        except:
            ips = []
            for ip in xo['ips']:
                ips.append( ip['ipv4'] )
            print xo['an'] , xo['sn'] , ','.join( ips )

    """
