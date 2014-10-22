# -*- coding: utf-8 -*-
import os
import os.path
import codecs
import sys

# work for file , read , create ,delete ,update ,find
class WorkProfile( object ):

    def __init__( self ):
        pass

    def pathf( self ,path ):
        if path == None or path == '':
            return './'
        else:
            abpath = os.path.abspath(sys.argv[0])
            if path[-1] == '/':
                return os.path.dirname(abpath)+'/'+path
            else:
                return os.path.dirname(abpath)+'/'+path+'/'


    def fileExist( self , path, fileName ):
        return os.path.exists( self.pathf(path) + fileName )

    def read( self , path , fileName ):
        fileCo = []
        with open( self.pathf( path )+ fileName , 'r') as fp :
            lines = fp.readlines()
            for line in lines:
                fileCo.append( line.split('\n')[0].strip() )
            fp.close()

        return fileCo


    def writeFile( self , path ,fileName , content ):
        with codecs.open( self.pathf( path )+ fileName , 'a' , 'utf-8') as fp :
            fp.write( content )
            fp.close()


    def deleteFile( self , path , fileName ):
        os.remove( self.pathf(path) + fileName )

    def fileSize ( self , path , fileName ):
        return os.path.getsize( self.pathf( path ) + fileName )

    def cleanFile( self ,path , fileName ):

        if self.fileExist( path,fileName ) and  self.fileSize( path, fileName ) > 0:

            try:
                fp = open( self.pathf(path)+fileName, 'w')
                fp.truncate()
                fp.close()
                return True
            except:
                return False



