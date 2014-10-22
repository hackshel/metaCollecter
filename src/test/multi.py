import multiprocessing
import easysql

def do_calculation(data):
    print data

def start_process():
    print 'Starting',multiprocessing.current_process().name

def getMetaCount( edb ,table ) :

    result = edb.cmdb_server_basic.getCounts('count')
    return result




if __name__=='__main__':


    db = { 'host' : 'localhost',
           'port' : 3306,
           'user' : 'root',
           'passwd' : 'Sina!Puppet!',
           'db' : 'metaDB2',
         }

    edb = easysql.Database( db )

    count = getMetaCount( edb , 'cmdb_servers_basic' )

    print count

    offset = 1000
    times = count[0]['count'] / offset
    if count[0]['count'] % offset != 0 :
        times = times + 1
    start = []
    for i in xrange( times ):
        start.append( offset * i  )

    print start

    inputs = zip(start , offset )
    print inputs

    inputs=list(range(10))
    print 'Inputs  :',inputs

    builtin_output=map(do_calculation,inputs)
    print 'Build-In :', builtin_output

    pool_size=multiprocessing.cpu_count()*2
    pool=multiprocessing.Pool(processes=pool_size,
        initializer=start_process,maxtasksperchild=2)

    pool_outputs=pool.map(do_calculation,inputs )
    pool.close()
    pool.join()

    print 'Pool  :',pool_outputs
