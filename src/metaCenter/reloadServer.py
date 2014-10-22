# -*- coding: utf-8 -*-
import os
import time


def reloadServers( fileName ):
    with open( fileName , 'r' ) as fp:
        lines = fp.readlines()
        for line in lines:
            d = {}
            r = line.split('\t')
            an = r[0].strip()
            sn = r[1].strip()
            rack = r[2].strip()
            ips = r[3].split('\n')[0].split(';')

            ip_list = []

            for ip in ips:
                ip_info = ip.split('-')
                if ip_info[0] == r'内网' or ip_info[0] == r'外网':
                    ip_list.append( ip_info[1] )


            d['an'] = an
            d['sn'] = sn
            d['rack'] = rack
            d['ips'] = ip_list


if __name__ == '__main__':
    b = time.time()
    reloadServers( 'sourceData/servers.txt' )
    e = time.time()

    print e - b
