#!/usr/bin/env python2.6
# coding: utf-8

import conf

import logging
import traceback
import logging.handlers
import time
from stat import ST_DEV, ST_INO

import os.path
import os
import sys

# DEFAULT_FORMAT = "%(levelcolor)s[%(asctime)s,%(process)d,%(filename)s,%(lineno)d,%(levelname)s]%(endcolor)s %(message)s"
DEFAULT_FORMAT = "[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s"

#DEFAULT_FORMAT = "[%(asctime)s] %(levelname)5s #%(process)5d   %(message)s"
DEFAULT_DATETIME_FORMAT = '%m%d-%H:%M:%S'

stdHandlerSet = set()

APPNAME = sys.argv[0]
APPNAME = APPNAME.split( '/' )[ -1 ]

if APPNAME.endswith( '.py' ):
    APPNAME = APPNAME[:-3]

if APPNAME == '-c':
    APPNAME = '_instantCommand'
    LOG_FILENAME = '_instantCommand'
else:
    if os.name != 'nt' :
        #LOG_FILENAME = os.path.join( conf.PATH['log_dir'], APPNAME+'.out' )
        LOG_FILENAME = os.path.join( '/tmp', APPNAME+'.out' )
    else :
        LOG_FILENAME = ''

# an util to prevent evaluating arguments of logging statement
def iflog( lvl ): return logger.getEffectiveLevel() <= lvl

def ifdebug():    return logger.getEffectiveLevel() <= logging.DEBUG
def ifinfo():     return logger.getEffectiveLevel() <= logging.INFO
def ifwarn():     return logger.getEffectiveLevel() <= logging.WARNING
def iferror():    return logger.getEffectiveLevel() <= logging.ERROR
def ifcritical(): return logger.getEffectiveLevel() <= logging.CRITICAL

logging.NOTIFIED = 25
logging.addLevelName( logging.NOTIFIED, 'NOTIFIED' )



class MyFormatter( logging.Formatter ):

    COLORS = dict(
            zip([ 'grey',
                  'red',
                  'green',
                  'yellow',
                  'blue',
                  'magenta',
                  'cyan',
                  'white',
            ], range(30, 38) )
    )
        
    _colordict = {
        'DEBUG'    : COLORS['blue'],
        'INFO'     : COLORS['green'],
        'WARNING'  : COLORS['yellow'],
        'ERROR'    : COLORS['red'],
        'CRITICAL' : COLORS['magenta'],
    }
    
    def format( self, record ) :
        record.levelcolor = '\033[%dm' % (self._colordict.get(record.levelname,0),)
        record.endcolor = '\033[0m'
        return logging.Formatter.format( self, record )
        
class ctimeFormatter( logging.Formatter ):
    
    def formatTime( self, record, datefmt=None ):
        return str(int(time.time()))





class MyLogger( logging.getLoggerClass() ):
    
    def notified( self, msg, *args, **kwargs ):
        return self.log( logging.NOTIFIED, msg, *args, **kwargs )


if os.name != 'nt' :
    logging.setLoggerClass( MyLogger )






def reset_defaults( appname = None ):
    
    global APPNAME
    global LOG_FILENAME
    
    APPNAME = appname if appname!=None else sys.argv[0]
    APPNAME = APPNAME.split( '/' )[ -1 ]
    
    if APPNAME.endswith( '.py' ):
        APPNAME = APPNAME[:-3]
        
    LOG_FILENAME = os.path.join( conf.PATH['log_dir'], APPNAME+'.out' )
    
    return

def getdefaultlogger( appname = None ):
    
    logname = appname or 'genlogger'
    
    # Set up a specific logger with our desired output level
    logger = logging.getLogger( logname )
    
    return logger



class S3LogHandler( logging.handlers.WatchedFileHandler ):
    """
    Fix the bug that stat checking after existence checking of log file
    raises an OSError
    r"""

    def emit(self, record):

        try:
            stat = os.stat(self.baseFilename)
            changed = (stat[ST_DEV] != self.dev) or (stat[ST_INO] != self.ino)
        except OSError, e:
            stat = None
            changed = 1


        # if not os.path.exists(self.baseFilename):
        #     stat = None
        #     changed = 1
        # else:
        #     stat = os.stat(self.baseFilename)
        #     changed = (stat[ST_DEV] != self.dev) or (stat[ST_INO] != self.ino)


        if changed and self.stream is not None:
            self.stream.flush()
            self.stream.close()
            self.stream = self._open()
            if stat is None:
                stat = os.stat(self.baseFilename)
            self.dev, self.ino = stat[ST_DEV], stat[ST_INO]
        logging.FileHandler.emit(self, record)


def createlogger ( appname = None, level = logging.DEBUG, 
                   format = None, formatter = logging.Formatter ):
    
    if appname != None :
        filename = os.path.join( conf.PATH['log_dir'], appname+'.out' )
    else :
        filename = LOG_FILENAME

    logname = appname or 'genlogger'
    
    # Set up a specific logger with our desired output level
    logger = logging.getLogger( logname )
    logger.setLevel( level )
    
    # Add the log message handler to the logger
    #
    # class logging.handlers.RotatingFileHandler
    #       (filename[, mode[, maxBytes[, backupCount[, encoding[, delay]]]]])
    # class logging.handlers.TimedRotatingFileHandler
    #       (filename[, when[, interval[, backupCount[, encoding[, delay
    #        [, utc]]]]]])
    #
    
    # handler = logging.handlers.RotatingFileHandler(
    #              LOG_FILENAME, maxBytes=20, backupCount=5)


    # WatchedFileHandler automatically switch log file back to <filename> if
    # log file is moved.
    handler = S3LogHandler( filename )

    # handler = logging.handlers.TimedRotatingFileHandler( filename,
    #                                                      when='S',
    #                                                      interval=10,)
    #                                                      # backupCount=10,)
    
    format = format or DEFAULT_FORMAT
    
    # create formatter
    # formatter = logging.Formatter( format, DEFAULT_DATETIME_FORMAT )
    _formatter = formatter( format )
    # formatter = MyFormatter( format, DEFAULT_DATETIME_FORMAT )
    
    # add formatter to ch
    handler.setFormatter(_formatter)
    
    logger.handlers = []
    logger.addHandler( handler )

    return logger

def add_std_handler( logger, stream = None, format = None, datefmt = None ):
    ''' Default stream is sys.stdout
    '''

    stream = stream or sys.stdout


    if stream in stdHandlerSet:
        return logger

    stdHandlerSet.add( stream )

    stdhandler = logging.StreamHandler( stream )
    stdhandler.setFormatter( 
            logging.Formatter( format or DEFAULT_FORMAT,
                               datefmt ) )

    logger.addHandler( stdhandler )

    return logger

def setloggerformat( format, datefmt = None ):
    
    logger = logging.getLogger('genlogger')
    
    formatter = logging.Formatter( format, datefmt )
    
    for handler in logger.handlers :
        handler.setFormatter(formatter)
    
    return logger

if os.name != 'nt' :
    logger = createlogger()
else :
    logger = None


def trace_warn( e ):
    logger.warn( traceback.format_exc() )
    logger.warn( repr( e ) )


def trace_error( e ):
    logger.error( traceback.format_exc() )
    logger.error( repr( e ) )


def stack_list( offset=0 ):
    offset += 1 # count this function as 1

    # list of ( filename, line-nr, in-what-function, statement )
    x = traceback.extract_stack()
    return x[ : -offset ]


def format_stack( stacks ):
    x = [ "{0}:{1} {3}".format( *xx ) for xx in stacks ]
    x = ' --- '.join( x )
    return x


def stack_str( offset=0 ):
    offset += 1 # count this function as 1
    return format_stack( stack_list( offset ) )


def deprecate( lgr=None, mes='' ):
    lgr = lgr or logger

    if mes != '':
        mes = mes + ' '
    lgr.warn( mes + "Deprecated: " + stack_str( offset=2 ) )


def setdefaultlogger():

    global logger

    #logger = getdefaultlogger()
    logger = createlogger()

    logger.debug( '  genlog Reopened' )

if __name__ == '__main__' :

    add_std_handler( logger )
    logger.debug( '123' )

    import glob

    # Log some messages
    for i in range(20):
        logger.debug('i = %d' % i)
    def foo ():
        logger.debug('print in %(funcName)s')
    createlogger('wahaha')
    for i in range(20):
        logger.debug('i = %d' % i)

    # See what files are created
    logfiles = glob.glob('%s*' % LOG_FILENAME)

    for filename in logfiles:
        print filename

