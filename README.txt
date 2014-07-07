pyClamd is a portable Python module to use the ClamAV antivirus engine on 
Windows, Linux, MacOSX and other platforms. It requires a running instance of 
the clamd daemon.


License:
pyClamd is released as open-source software under the LGPLv3 (or later) license.

Download: 
see http://xael.org/norman/python/pyclamd/



How to install clamd:

    * For Windows: you need an unofficial version from http://hideout.ath.cx/clamav/ 
      or http://oss.netfarm.it/clamav/ (http://w32.clamav.net does not provide 
      clamd anymore, and neither does ClamWin)
          o Before running clamd, edit clamd.conf and make sure it is configured 
            to use a TCP port instead of a Unix socket: LocalSocket should be 
            disabled, TCPSocket and TCPAddr should be enabled.
    * For MacOSX: you may install ClamXav, and then run clamd from /usr/local/clamXav/sbin.
    * For other operating systems such as Linux and *BSD: http://www.clamav.org/download

 

How to run clamd as a service on Windows:

See http://www.andornot.com/blog/post/How-to-set-up-ClamAV-as-a-Windows-Service-to-scan-file-streams-on-demand.aspx 
or http://www.google.com/search?q=clamd+windows+service

There used to be instructions on http://www.asspsmtp.org/wiki/ClamAV_Win32 to 
use either runclamd or the NJH Power Tools, but the website is not available 
anymore.


How to use pyClamd:

See source code or Alexandre Norman's website: 
http://xael.org/norman/python/pyclamd/


Here is an example on Unix:


>>> import pyclamd
>>> # Create object for using unix socket or network socket
>>> cd = pyclamd.ClamdAgnostic()
>>> # test if server is OK
>>> cd.ping()
True
>>> # print version
>>> print "Version : \n{0}".format(cd.version())
Version : 
ClamAV 0.98.1/19122/Sun Jun 22 08:24:11 2014
>>> # force a db reload
>>> cd.reload()
u'RELOADING'
>>> # print stats
>>> print "{0}".format(cd.stats())
POOLS: 1

STATE: VALID PRIMARY
THREADS: live 1  idle 0 max 12 idle-timeout 30
QUEUE: 0 items
	STATS 0.000048
MEMSTATS: heap 6.098M mmap 0.000M used 3.770M free 2.337M releasable 0.132M pools 1 pools_used 268.122M pools_total 268.136M
END
>>> # write test file with EICAR test string
>>> open('/tmp/EICAR','w').write(cd.EICAR())
>>> # write test file without virus pattern
>>> open('/tmp/NO_EICAR','w').write('no virus in this file')
>>> # scan files
>>> print "{0}".format(cd.scan_file('/tmp/EICAR'))
{u'/tmp/EICAR': ('FOUND', 'Eicar-Test-Signature')}
>>> print "{0}".format(cd.scan_file('/tmp/NO_EICAR'))
None
>>> # scan a stream
>>> print "{0}".format(cd.scan_stream(cd.EICAR()))
{u'stream': ('FOUND', 'Eicar-Test-Signature')}
