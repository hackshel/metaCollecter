import httplib
import urllib
import json
import pprint
import ssl
import re
import time

class core( object ):

    defaultParams = {
        'ignore_error': 'false',
        'output' : 'json',
        'timeout' : '10',
        'user' : 'xiaoyue1',
        'key' : 'SJc4FekPGBV2uRCrWCHtAGdpIrB4P2S7',
        'method' : 'sync',
    }


    def __init__( self, args=None  ):

        if args == None:
            self.params = self.defaultParams
        else:
            self.params = self._argsCheck( args, self.defaultParams )

        self.host = 'api.c.sina.com'
        self.url  = '/add_api_range_json_scp.php'
        self.header = {  "Content-type": "application/x-www-form-urlencoded",
                         "Accept": "text/json" }


    def _argsCheck( self , user_args,default ):

        d = {}
        for key ,val in default.items():
            if user_args.has_key( key ):
                d[key] = user_args[key]
            else:
                d[key] = default[key]
        return d


    def get( self ,ips,cmd ):

        result = []

        if len( ips ) > 0:
            self.params['ip'] = ','.join(ips)
        else:
            self.params['ip'] = ips[0]

        self.params['cmd'] = cmd

#        if len( ips ) > 1 :
        try:
            conn = httplib.HTTPSConnection( self.host  ,timeout=2)
            conn.request( 'POST' , '/add_api_range_json_scp.php', urllib.urlencode(self.params), self.header )
            response = conn.getresponse()
            if response.status == 200:
                res = json.loads('[' + response.read().replace('}','},')[:-1] +']')
                #pprint.pprint( res )
                time.sleep(10)
                for r in res:
                    try:
                        rr = r['RETURN'].split('\n')[0]
                        #print rr
                        if self.params['method'] == 'sync':
                            if json.loads(rr)['result'] == '' :
                                return {'err':'NO output'}
                            else:
                                return self.resultClean(json.loads(rr)['result'])
                        else:
                            callbackURL = rr.split('\n')[0].split('[')[1].split(']')[0]
                            #time.sleep(5)
                            #return self.callback( callbackURL )
                            #print self.callback( callbackURL )
                            result.append(self.callback( callbackURL ))
                    except KeyError:
                        #return res
                        result.append( res )
            else:
                return {'err':'HTTP Error, Code'+ response.status }

        except ssl.SSLError:
             return {'err':'time out' }
        except:
             return {'err':'unknown error'}

        return result

#        else:
#            try:
#                conn = httplib.HTTPSConnection( self.host  ,timeout=2)
#                conn.request( 'POST' , '/add_api_range_json.php', urllib.urlencode(self.params), self.header )
#                response = conn.getresponse()
#                if response.status == 200:
#                    res = json.loads(response.read())
#                    print res
#                    try:
#                        rr = res['RETURN']
#                        if self.params['method'] == 'sync':
#                            if json.loads(rr)['result'] == '' :
#                                return {'err':'NO output'}
#                            else:
#                                return self.resultClean(json.loads(rr)['result'])
#                        else:
#                            callbackURL = rr.split('\n')[0].split('[')[1].split(']')[0]
#                            time.sleep(5)
#                            return self.callback( callbackURL )
#                    except KeyError:
#                        return res
#                else:
#                    return {'err':'HTTP Error, Code'+ response.status }
#            except ssl.SSLError:
#                return {'err':'time out' }
#            except:
#                return {'err':'unknown error'}

    def callback( self , url ):

        #print url
        url = url.split('/')

        try:
            conn = httplib.HTTPSConnection( self.host )
            conn.request('GET','/'+url[3] )
            response = conn.getresponse()
            if response.status == 200:
                res = json.loads(response.read())
                #pprint.pprint( res )
                if res['result'] == '':
                    return {'err':'callback NO output'}
                else:
                    return self.resultClean( res['result'] )
            else:
                return {'err':'HTTP Error, Code'+ response.status }
        except:
            pass

    def resultClean( self , result ):
        if result.startswith('\x1b'):
            rr = result.split('\x07')[1].split('\n')
            for x in rr:
                if x == '':
                    rr.remove( x )
            return rr[0]
        else:
            return result.split('\n')[0]


if __name__ == '__main__':
    #curl = core( '202.106.184.232' , "'/usr/bin/snmpwalk -v 2c -c \"bdHH&xbS\" 10.55.254.40 sysDescr'")
    #curl = core( '218.30.13.62' )
    curl = core( {'method':'async' } )
    #res = curl.get( ['10.75.28.247'] ,"sudo python /usr/local/meta/metaCollecter.py reload " ) 
    #res = curl.get( ['10.75.18.139'] ,"sudo python /usr/local/meta/metaCollecter.py post " ) 
    #pprint.pprint( eval(res[0]) )
    #pprint.pprint( curl.get( ['60.28.228.88','10.13.8.42'],"sudo python /usr/local/meta/metaCollecter.py reload " ) )
    #pprint.pprint( curl.get( ['60.28.228.88'],"sudo uname -a" ) )
    #pprint.pprint( curl.get( ['10.13.8.42'],"sudo uname -a" ) )
    #pprint.pprint( curl.get( ['10.218.17.4'],"sudo uname -a" ))
    #pprint.pprint( curl.get( ['172.16.11.98'],"sudo uname -a" ))
    #pprint.pprint( curl.get( ['114.80.223.229'],"sudo python /usr/local/meta/metaCollecter.py reload " ))
    #pprint.pprint( curl.get( ['60.28.2.15'],"sudo python /usr/local/meta/metaCollecter.py post " ))
    #pprint.pprint( curl.get( ['60.28.2.15'],"python -V " ))
    pprint.pprint( curl.get( ['123.125.104.132'],"sudo python /usr/local/meta/metaCollecter.py reload " ))
    #pprint.pprint( eval(curl.get( ['10.13.3.195'],"sudo python /usr/local/meta/metaCollecter.py reload " )))
    #pprint.pprint( curl.get( ['10.77.112.226'],"sudo python /usr/local/meta/metaCollecter.py reload " ))
    #pprint.pprint( curl.get( ['219.232.247.28'],"sudo python /usr/local/meta/metaCollecter.py reload " ))
    #pprint.pprint( curl.get( ['10.83.8.59'],"sudo python /usr/local/meta/metaCollecter.py reload " ))
    #pprint.pprint( curl.get( ['10.77.109.113'],"sudo rsync -av /etc/sudoers root@10.210.66.81::resolv" ))
    #pprint.pprint( curl.get( ['10.75.1.59'],"sudo rsync -av  /usr/local/meta/conf/post_config.py root@10.210.66.81::resolv" ))
    #pprint.pprint( curl.get( ['60.28.113.161'],"python -V" ))
    #pprint.pprint( curl.get( ['218.57.9.118'],"whoami" ))
    #pprint.pprint( curl.get( '202.108.3.132' ,"sudo uname -a" ) )
    #print curl.get(  "uname -a" )


