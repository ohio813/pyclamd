#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyclamd

# Create object for using unix socket or network socket
cd = pyclamd.ClamdAgnostic()

# test if server is OK
cd.ping()


# print version
print "Version : \n{0}\n".format(cd.version())

# force a db reload
cd.reload()

# print stats
print "\n{0}\n".format(cd.stats())

# write test file with EICAR test string
open('/tmp/EICAR','w').write(cd.EICAR())

# write test file without virus pattern
open('/tmp/NO_EICAR','w').write('no virus in this file')

# scan files
print "\n{0}\n".format(cd.scan_file('/tmp/EICAR'))
print "\n{0}\n".format(cd.scan_file('/tmp/NO_EICAR'))

# scan a stream
print "\n{0}\n".format(cd.scan_stream(cd.EICAR()))

