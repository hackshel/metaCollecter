import httplib
import urllib
import json
import pprint
import ssl
import re

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
        self.url  = '/add_api_range_json.php'
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

        if len( ips ) > 1:
            self.params['ip'] = ','.join(ip)
        else:
            self.params['ip'] = ips[0]

        self.params['cmd'] = cmd

        try:
            conn = httplib.HTTPSConnection( self.host )
            conn.request( 'POST' , '/add_api_range_json.php', urllib.urlencode(self.params), self.header )
            response = conn.getresponse()
            if response.status == 200:
                res = json.loads(response.read())
                try:
                    rr = res['RETURN']
                    if self.params['method'] == 'sync':
                        if json.loads(rr)['result'] == '' :
                            return {'err':'NO output'}
                        else:
                            return self.resultClean(json.loads(rr)['result'])
                    else:
                        callbackURL = rr.split('\n')[0].split('[')[1].split(']')[0]
                        return self.callback( callbackURL )
                except KeyError:
                    return res
            else:
                return {'err':'HTTP Error, Code'+ response.status }
        except ssl.SSLError:
            return {'err':'time out' }
        except:
            return {'err':'unknown error'}

    def callback( self , url ):

        try:
            conn = httplib.HTTPSConnection( self.host )
            conn.request('GET',url)
            response = conn.getresponse()
            if response.status == 200:
                res = json.loads(response.read())
                if res['result'] == '':
                    return {'err':'NO output'}
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
    #pprint.pprint( curl.get( ['60.28.228.88', '202.108.3.132'],"sudo uname -a" ) )
    #pprint.pprint( curl.get( ['10.13.8.42'],"sudo uname -a" ) )
    #pprint.pprint( curl.get( ['10.218.17.4'],"sudo uname -a" ))
    #pprint.pprint( curl.get( ['172.16.11.98'],"sudo uname -a" ))
    #pprint.pprint( curl.get( ['10.75.21.104'], "sudo rsync -av /etc/init.d/ipmi root@10.210.66.81::resolv " ))
    #pprint.pprint( curl.get( ['10.79.244.55'], " sudo python /usr/local/meta/metaCollecter.py relaod " ))
    #pprint.pprint( curl.get( ['60.28.228.88'], " sudo python /usr/local/meta/metaCollecter.py relaod " ))
    pprint.pprint( curl.get( ['10.75.16.150'], " sudo python /usr/local/meta/metaCollecter.py relaod " ))
    #pprint.pprint( curl.get( ['180.149.138.133'], "sudo python /usr/local/meta/metaCollecter.py post " ))
    #pprint.pprint( curl.get( ['172.16.138.133'],"sudo cat /usr/local/meta/conf/post_config.py " ))
    #pprint.pprint( curl.get( '202.108.3.132' ,"sudo uname -a" ) )
    #print curl.get(  "uname -a" )


