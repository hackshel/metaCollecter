# -*- coding: utf-8 -*-
import pprint

def readFile( fileName ):
    r = []
    with open( fileName+'.txt' , 'r' ) as fp:
        lines = fp.readlines()
        for line in lines:
            an , idc , ip = line.split('\t')
            r.append( {'an':an , 'idc':idc , 'ip': ip } )

    return r

if __name__ == '__main__':

    idcList = [ '永丰','土城','七星岗','西单','亦庄','北显','沙溪','静安','雍和宫','华苑','丰台', 'unknown' ]

    servers = []
    with open( 'result20140412144238.txt' , 'r' ) as fp:
        lines = fp.readlines()
        for line in lines:
            an , ip =  line.split()
            d = {'an': an , 'ip':ip }
            servers.append( d )


    for idc in idcList :
        result = readFile( idc )
        print idc
        #pprint.pprint( result )
        for r in result:
            for s in servers:
                if r['an'] == s['an']:
                    servers.remove( s )


    pprint.pprint( servers )
