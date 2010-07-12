#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# LICENSE:
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free 
# Software  Foundation; either version 3 of the License, or (at your option) any
# later version. See http://www.gnu.org/licenses/lgpl-3.0.txt.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more 
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 675 Mass Ave, Cambridge, MA 02139, USA.
#------------------------------------------------------------------------------
# CHANGELOG:
# 2006-07-15 v0.1.1 AN: - released version
# 2007-10-09 v0.2.0 PL: - fixed error with deprecated string exceptions
#					    - added optional timeout to sockets to avoid blocking 
#						  operations
# 2010-07-11 v0.2.1 AN: - change all raise exception (was deprecated), license 
#						  change to LGPL
# 2010-07-12 v0.3.0 AN: - change API to class model
#                       - using INSTREAM scan method instead of the deprecated STREAM
#                       - added MULTISCAN method
#------------------------------------------------------------------------------
# TODO:
# - improve tests for Win32 platform (avoid to write EICAR file to disk, or
#   protect it somehow from on-access AV, inside a ZIP/GZip archive isn't enough)
# - use SESSION/END commands to launch several scans in one session
#   (for example provide session mode in a Clamd class)
# - add support for RAWSCAN and MULTISCAN commands ?
# ? Maybe use os.abspath to ensure scan_file uses absolute paths for files
#------------------------------------------------------------------------------
# Documentation : http://www.clamav.net/doc/latest/html/node28.html

"""
pyclamd.py - v0.3.0 - 2010.07.12

Author : Alexandre Norman - norman()xael.org
Contributors :
  Philippe Lagadec - philippe.lagadec()laposte.net
  Thomas Kastner - tk()underground8.com
Licence : LGPL

Usage :

Test strings :
^^^^^^^^^^^^

>>> import pyclamd
>>> cd = clamd.clamd_unix_socket()
>>> cd.ping()
True
>>> cd.version().split()[0]
'ClamAV'
>>> cd.reload()
'RELOADING'
>>> cd.stats()
'POOLS: 1'
>>> open('/tmp/EICAR','w').write(cd.EICAR())
>>> cd.scan_file('/tmp/EICAR')
{'/tmp/EICAR': 'Eicar-Test-Signature'}
>>> cd.scan_stream(cd.EICAR())
{'stream': 'Eicar-Test-Signature'}
"""


import socket
import types
import struct
import string

############################################################################

class BufferTooLongError(ValueError):
	pass

class ScanError(IOError):
	pass


############################################################################


class clamd_generic(object):
    """
    Abstract class for clamd
    """
    def __init__(self):
        """
        class initialisation, this class should not be used
        """
        self.unix_socket = None
        self.host = None
        self.port = None
        self.timeout = None
        self.clamd_socket = None
        return


    def EICAR(self):
        """
        returns Eicar test string
        """
        # Eicar test string (encoded for skipping virus scanners)
        EICAR = 'WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5E' \
                'QVJELUFOVElWSVJVUy1URVNU\nLUZJTEUhJEgrSCo=\n'.decode('base64')
        return EICAR
        

    def ping(self):
        """
        Send a PING to the clamav server, which should reply
        by a PONG.

        return: True if the server replies to PING

        May raise:
          - ScanError: if the server do not reply by PONG
        """

        self.__init_socket__()
        try:
            self.__send_command('PING')
            result = self.__recv_response()
            self.__close_socket()
        except socket.error:
            raise ScanError('Could not ping clamd server')

        if result == 'PONG':
            return True
        else:
            raise ScanError('Could not ping clamd server')
        return


    
    def version(self):
        """
        Get Clamscan version

        return: (string) clamscan version

        May raise:
          - ScanError: in case of communication problem
        """
        self.__init_socket__()
        try:
            self.__send_command('VERSION')
            result = self.__recv_response()
            self.__close_socket()
        except socket.error:
            raise ScanError('Could not get version information from server')

        return result


    def stats(self):
        """
        Get Clamscan stats

        return: (string) clamscan stats

        May raise:
          - ScanError: in case of communication problem
        """
        self.__init_socket__()
        try:
            self.__send_command('STATS')
            result = self.__recv_response()
            self.__close_socket()
        except socket.error:
            raise ScanError('Could not get version information from server')

        return result

    
    def reload(self):
        """
        Force Clamd to reload signature database

        return: (string) "RELOADING"

        May raise:
          - ScanError: in case of communication problem
        """


        try:
            self.__init_socket__()
            self.__send_command('RELOAD')
            result = self.__recv_response()
            self.__close_socket()
            
        except socket.error:
            raise ScanError('Could probably not reload signature database')

        return result


    
    def shutdown(self):
        """
        Force Clamd to shutdown and exit

        return: nothing

        May raise:
          - ScanError: in case of communication problem
        """
        try:
            self.__init_socket__()
            self.__send_command('SHUTDOWN')
            result = self.__recv_response()
            self.__close_socket()
        except socket.error:
            raise ScanError('Could probably not shutdown clamd')


    
    def scan_file(self, file):
        """
        Scan a file or directory given by filename and stop on first virus or error found.
        Scan with archive support enabled.

        file (string) : filename or directory (MUST BE ABSOLUTE PATH !)

        return either :
          - (dict): {filename1: "virusname"}
          - None: if no virus found

        May raise :
          - ScanError: in case of communication problem
          - socket.timeout: if timeout has expired
        """

        assert type(file) in types.StringTypes, 'Wrong type for [file], should be a string [was {0}]'.format(type(file))

        try:
            self.__init_socket__()
            self.__send_command('SCAN %s' % file)
        except socket.error:
            raise ScanError('Unable to scan %s' % file)

        result='...'
        dr={}
        while result:
            try:
                result = self.__recv_response()
            except socket.error:
                raise ScanError('Unable to scan %s' % file)

            if len(result) > 0:
                filename, reason, status = self.__parse_response(result)

                if status == 'ERROR':
                    raise ScanError(reason)
                elif status == 'FOUND':
                    dr[filename] = reason

        self.__close_socket()
        if not dr:
            return None
        return dr

    



    def multiscan_file(self, file):
        """
        Scan a file or directory given by filename using multiple threads (faster on SMP machines).
        Do not stop on error or virus found.
        Scan with archive support enabled.

        file (string): filename or directory (MUST BE ABSOLUTE PATH !)

        return either :
          - (dict): {filename1: ('FOUND', 'virusname'), filename2: ('ERROR', 'reason')}
          - None: if no virus found

        May raise:
          - ScanError: in case of communication problem
        """
        assert type(file) in types.StringTypes, 'Wrong type for [file], should be a string [was {0}]'.format(type(file))

        try:
            self.__init_socket__()
            self.__send_command('MULTISCAN %s' % file)
        except socket.error:
            raise ScanError('Unable to scan %s' % file)

        result='...'
        dr={}
        while result:
            try:
                result = self.__recv_response()
            except socket.error:
                raise ScanError('Unable to scan %s' % file)

            if len(result) > 0:
                filename, reason, status = self.__parse_response(result)

                if status == 'ERROR':
                    dr[filename] = ('ERROR', '{0}'.format(reason))
                    
                elif status == 'FOUND':
                    dr[filename] = ('FOUND', '{0}'.format(reason))

        self.__close_socket()
        if not dr:
            return None
        return dr







    def contscan_file(self, file):
        """
        Scan a file or directory given by filename
        Do not stop on error or virus found.
        Scan with archive support enabled.

        file (string): filename or directory (MUST BE ABSOLUTE PATH !)

        return either :
          - (dict): {filename1: ('FOUND', 'virusname'), filename2: ('ERROR', 'reason')}
          - None: if no virus found

        May raise:
          - ScanError: in case of communication problem
        """
        assert type(file) in types.StringTypes, 'Wrong type for [file], should be a string [was {0}]'.format(type(file))

        try:
            self.__init_socket__()
            self.__send_command('CONTSCAN %s' % file)
        except socket.error:
            raise ScanError('Unable to scan %s' % file)

        result='...'
        dr={}
        while result:
            try:
                result = self.__recv_response()
            except socket.error:
                raise ScanError('Unable to scan %s' % file)

            if len(result) > 0:
                filename, reason, status = self.__parse_response(result)

                if status == 'ERROR':
                    dr[filename] = ('ERROR', '{0}'.format(reason))
                    
                elif status == 'FOUND':
                    dr[filename] = ('FOUND', '{0}'.format(reason))

        self.__close_socket()
        if not dr:
            return None
        return dr



    def scan_stream(self, buffer):
        """
        Scan a buffer

        buffer (string): buffer to scan

        return either:
          - (dict): {filename1: "virusname"}
          - None: if no virus found

        May raise :
          - BufferTooLongError: if the buffer size exceeds clamd limits
          - ScanError: in case of communication problem
        """
        assert type(buffer) in types.StringTypes, 'Wrong type for [buffer], should be a string [was {0}]'.format(type(buffer))

        try:
            self.__init_socket__()
            self.__send_command('INSTREAM')

            max_chunk_size = 1024 # MUST be < StreamMaxLength in /etc/clamav/clamd.conf

            chunks_left = buffer
            while len(chunks_left)>0:
                chunk = chunks_left[:max_chunk_size]
                chunks_left = chunks_left[max_chunk_size:]

                size = struct.pack('!L', len(chunk))
                self.clamd_socket.send('{0}{1}'.format(size, chunk))

            self.clamd_socket.send(struct.pack('!L', 0))
                
            
        except socket.error:
            raise ScanError('Unable to scan stream')


        result='...'
        dr={}
        while result:
            try:
                result = self.__recv_response()
            except socket.error:
                raise ScanError('Unable to scan stream')

            if len(result) > 0:
                
                if result == 'INSTREAM size limit exceeded. ERROR':
                    raise BufferTooLongError,'INSTREAM size limit exceeded. ERROR'

                filename, reason, status = self.__parse_response(result)

                if status == 'ERROR':
                    raise ScanError(reason)
                elif status == 'FOUND':
                    dr[filename] = reason

        self.__close_socket()
        if not dr:
            return None
        return dr





    
    def __send_command(self, cmd):
        """
        `man clamd` recommends to prefix commands with z, but we will use \n
        terminated strings, as python<->clamd has some problems with \0x00
        """

        cmd = 'n%s\n' % cmd 
        self.clamd_socket.send(cmd)
        return
    

    def __recv_response(self):
        """
        receive response from clamd and strip all whitespace characters
        """

        response = self.clamd_socket.recv(20000)
        response = response.strip()
        return response


    def __close_socket(self):
        """
        close clamd socket
        """
        self.clamd_socket.close()
        return
    

    def __parse_response(self, msg):
        """
        parses responses for SCAN, CONTSCAN, MULTISCAN and STREAM commands.
        """

        msg = msg.strip()
        filename = msg.split(': ')[0]
        left = msg.split(': ')[1:]
        if type(left) in types.StringTypes:
            result = left
        else:
            result = string.join(left, ': ')
            
        if result != 'OK':
            parts = result.split()
            reason = ' '.join(parts[:-1])
            status = parts[-1]
        else:
            reason, status = '', 'OK'

        return filename, reason, status




############################################################################


class clamd_unix_socket(clamd_generic):
    """
    Class for using clamd with an unix socket
    """
    def __init__(self, filename="/var/run/clamav/clamd.ctl", timeout=None):
        """
        class initialisation

        filename (string) : unix socket filename
        """
        assert type(filename) in types.StringTypes, 'Wrong type for [filename], should be a string [was {0}]'.format(type(filename))
        assert type(timeout) in (types.IntType, types.NoneType), 'Wrong type for [timeout], should be either None or an int [was {0}]'.format(type(timeout))

        clamd_generic.__init__(self)
        
        self.unix_socket = filename

        return


    def __init_socket__(self):
        """
        internal use only
        """
        try:
            self.clamd_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.clamd_socket.connect(self.unix_socket)
            if self.timeout is not None:
                self.clamd_socket.settimeout(clamd_timeout)
        except socket.error:
            raise ScanError('Could not reach clamd using unix socket (%s)' % 
                        (self.unix_socket))        
        return
    

############################################################################


class clamd_network_socket(clamd_generic):
    """
    Class for using clamd with a network socket
    """
    def __init__(self, host='127.0.0.1', port=3310, timeout=None):
        """
        class initialisation

        host (string) : hostname or ip address
        port (int) : TCP port
        timeout (int or None) : socket timeout
        """
        assert type(host) in types.StringTypes, 'Wrong type for [host], should be a string [was {0}]'.format(type(host))
        assert type(port) in types.IntType, 'Wrong type for [port], should be an int [was {0}]'.format(type(port))
        assert type(timeout) in (types.IntType, types.NoneType), 'Wrong type for [timeout], should be either None or an int [was {0}]'.format(type(timeout))
        clamd_generic.__init__(self)
        
        self.host = host
        self.port = port
        self.timeout = timeout

        return


    def __init_socket__(self):
        """
        internal use only
        """
        try:
            self.clamd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clamd_socket.connect((self.host, self.port))
            if self.timeout is not None:
                self.clamd_socket.settimeout(clamd_timeout)

        except socket.error:
            raise ScanError('Could not reach clamd using network (%s, %s)' % 
                        (self.host, self.port))

        return

    

############################################################################


def __non_regression_test():
	"""
	This is for internal use
	"""
	import doctest
	doctest.testmod()
	return
	

############################################################################


# MAIN -------------------
if __name__ == '__main__':
	
	__non_regression_test()



#<EOF>###########################################################################
