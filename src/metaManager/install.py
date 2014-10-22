# coding: utf-8
import os
import pprint
import urllib2
import sys
import tarfile
import shutil

def minest( ips ):

    mini = 100
    mini_obj = {}
    for ip in ips:
        if float(ip['speed']) < mini:
            mini = float((ip['speed']))
            mini_obj['name'] = ip['name']
            mini_obj['simple_name'] = ip['simple_name']
            mini_obj['ip'] = ip['ip']

    return mini_obj

def writeConfig( path ):

    for ip in ips:
        n = os.popen( 'ping -c 1 -W 1 ' + ip['ip'] )
        ip['speed'] = n.readlines()[-1].strip().split('=')[1].split('/')[1].strip()

    mini = minest( ips )
    try:
        fp = open( path + '/post_config.py' , 'w' )
        fp.write("# coding: utf-8\n")
        fp.write("POST_HOST = '"  + mini['ip'] + "'\n")
        fp.write("POST_HOST_NAME = '"  + mini['name'].encode('utf-8') + "'\n")
        fp.write("POST_HOST_SIMPLE = '"  + mini['simple_name'] + "'\n")
        fp.write("POST_PORT = 10086\n")
        fp.write("POST_URL = '/post_serverinfo'\n")
        fp.write("POST_HEADER = { 'Content-type' : 'application/json','Accept' : 'text/json'}\n")

        fp.close()
        print 'configure config file ... OK'
    except:
        print 'conn\'t open file' + path +'/post_config.py'


def download( package ):

    for ip in ips:
        n = os.popen( 'ping -c 1 -W 1 ' + ip['ip'] )
        ip['speed'] = n.readlines()[-1].strip().split('=')[1].split('/')[1].strip()

    mini = minest( ips )
    mini['ip'] = '10.210.66.81:8020'

    if package == 'meta':
        url = 'http://'+mini['ip']+'/meta.tar.gz'
    elif package == 'webserver':
        url = 'http://'+mini['ip']+'/webserver.tar.gz'

    req = urllib2.Request( url )

    f = urllib2.urlopen( req )

    block = f.read()
    sys.stdout.write(' saveing block ... ' )

    fobj = open( package+'.tar.gz' , 'wb')

    fobj.write( block )

    sys.stdout.write('done.')


def extraTar( path , fileName ) :

    tar = tarfile.open( path +'/' + fileName )

    names = tar.getnames()


    for name in names:
        tar.extract( name , path='/tmp/' )

    tar.close()

    #shutil.move( '/tmp/meta', '/opt/meta')





if __name__ == '__main__':





    ips = [ {'name':u'永丰','simple_name':'YF.BJ' ,'ip':'10.75.6.31'},
            {'name':u'土城','simple_name':'TC.BJ'  ,'ip':'123.125.106.190'},
            {'name':u'七星岗','simple_name':'QXG.GZ'  ,'ip':'10.71.6.46'},
            {'name':u'西单','simple_name':'XD.BJ'  ,'ip':'10.55.30.63'},
            {'name':u'亦庄','simple_name':'YZ.BJ' ,'ip':'10.39.2.118'},
            {'name':u'北显','simple_name':'BX.BJ'  ,'ip':'10.13.8.106'},
            {'name':u'沙溪','simple_name':'SX.GZ' ,'ip':'172.16.93.10'},
            {'name':u'静安','simple_name':'GA.BJ' ,'ip':'10.69.2.50'},
            {'name':u'雍和宫','simple_name':'YHG.BJ' ,'ip':'172.16.35.160'},
            {'name':u'华苑','simple_name':'BY.TJ' ,'ip':'10.27.16.21'},
            {'name':u'丰台移动','simple_name':'.FTYD.BJ' ,'ip':'10.17.16.21'}
          ]

    if len(sys.argv)>=2 and sys.argv[1]:
        if sys.argv[1] == 'configure':

            writeConfig('/usr/local/meta/conf' )
    else:

        download( 'meta' )

        extraTar( './' , 'meta.tar.gz' )

        writeConfig('/tmp/meta/conf' )

        shutil.move( '/tmp/meta' , '/usr/local/' )

        os.remove( './meta.tar.gz' )
